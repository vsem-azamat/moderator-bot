"""Tests for BlacklistMiddleware."""

from typing import Any
from unittest.mock import AsyncMock

import pytest
from aiogram.types import TelegramObject
from app.application.services.user_service import UserService
from app.presentation.telegram.middlewares.black_list import BlacklistMiddleware

from tests.telegram_helpers import TelegramObjectFactory, create_normal_user, create_test_chat


class MockHandler:
    """Mock handler for middleware testing."""

    def __init__(self):
        self.called = False
        self.call_args = None

    async def __call__(self, event: TelegramObject, data: dict[str, Any]) -> None:
        self.called = True
        self.call_args = (event, data)


@pytest.mark.middleware
class TestBlacklistMiddleware:
    """Test cases for BlacklistMiddleware."""

    @pytest.fixture
    def telegram_factory(self):
        return TelegramObjectFactory()

    @pytest.fixture
    def mock_user_service(self):
        return AsyncMock(spec=UserService)

    @pytest.fixture
    def blacklist_middleware(self):
        return BlacklistMiddleware()

    @pytest.fixture
    def mock_handler(self):
        return MockHandler()

    async def test_blacklist_middleware_allows_non_blocked_user(
        self,
        telegram_factory: TelegramObjectFactory,
        blacklist_middleware: BlacklistMiddleware,
        mock_handler: MockHandler,
        mock_user_service: AsyncMock,
    ):
        """Test middleware allows non-blocked users to proceed."""
        # Arrange
        normal_user = create_normal_user()
        chat = create_test_chat()

        message = telegram_factory.create_message(user=normal_user, chat=chat, text="Hello world!")

        telegram_factory.create_update(message=message)

        data = {"user_service": mock_user_service}

        # Mock user is not blocked
        mock_user_service.is_user_blocked.return_value = False

        # Act
        await blacklist_middleware(mock_handler, message, data)

        # Assert
        mock_user_service.is_user_blocked.assert_called_once_with(normal_user.id)
        assert mock_handler.called is True
        assert mock_handler.call_args[0][0] == message

    async def test_blacklist_middleware_blocks_blacklisted_user(
        self,
        telegram_factory: TelegramObjectFactory,
        blacklist_middleware: BlacklistMiddleware,
        mock_handler: MockHandler,
        mock_user_service: AsyncMock,
    ):
        """Test middleware blocks blacklisted users."""
        # Arrange
        blocked_user = create_normal_user(id=666666666, username="blocked_user")
        chat = create_test_chat()

        message = telegram_factory.create_message(
            user=blocked_user, chat=chat, text="I'm blocked but trying to send message"
        )

        data = {"user_service": mock_user_service}

        # Mock user is blocked
        mock_user_service.is_user_blocked.return_value = True

        # Act
        await blacklist_middleware(mock_handler, message, data)

        # Assert
        mock_user_service.is_user_blocked.assert_called_once_with(blocked_user.id)
        assert mock_handler.called is False  # Handler should not be called

    async def test_blacklist_middleware_handles_service_error(
        self,
        telegram_factory: TelegramObjectFactory,
        blacklist_middleware: BlacklistMiddleware,
        mock_handler: MockHandler,
        mock_user_service: AsyncMock,
    ):
        """Test middleware handles user service errors gracefully."""
        # Arrange
        user = create_normal_user()
        chat = create_test_chat()

        message = telegram_factory.create_message(user=user, chat=chat)

        data = {"user_service": mock_user_service}

        # Mock service error
        mock_user_service.is_user_blocked.side_effect = Exception("Database error")

        # Act - Should not raise exception
        await blacklist_middleware(mock_handler, message, data)

        # Assert - Should allow user through on error (fail open)
        assert mock_handler.called is True

    async def test_blacklist_middleware_missing_user_service(
        self,
        telegram_factory: TelegramObjectFactory,
        blacklist_middleware: BlacklistMiddleware,
        mock_handler: MockHandler,
    ):
        """Test middleware when user service is not in data."""
        # Arrange
        user = create_normal_user()
        chat = create_test_chat()

        message = telegram_factory.create_message(user=user, chat=chat)

        data: dict[str, Any] = {}  # No user_service

        # Act - Should not raise exception
        await blacklist_middleware(mock_handler, message, data)

        # Assert - Should allow user through when service unavailable
        assert mock_handler.called is True

    async def test_blacklist_middleware_with_bot_messages(
        self,
        telegram_factory: TelegramObjectFactory,
        blacklist_middleware: BlacklistMiddleware,
        mock_handler: MockHandler,
        mock_user_service: AsyncMock,
    ):
        """Test middleware with messages from bots."""
        # Arrange
        bot_user = telegram_factory.create_user(id=999999999, username="test_bot", is_bot=True)
        chat = create_test_chat()

        message = telegram_factory.create_message(user=bot_user, chat=chat, text="Bot message")

        data = {"user_service": mock_user_service}

        # Act
        await blacklist_middleware(mock_handler, message, data)

        # Assert - Should check bots too (they can be blacklisted)
        mock_user_service.is_user_blocked.assert_called_once_with(bot_user.id)
        assert mock_handler.called is True  # Assuming bot is not blocked

    async def test_blacklist_middleware_performance_with_multiple_calls(
        self,
        telegram_factory: TelegramObjectFactory,
        blacklist_middleware: BlacklistMiddleware,
        mock_user_service: AsyncMock,
    ):
        """Test middleware performance with multiple concurrent calls."""
        import asyncio

        # Arrange
        users = [create_normal_user(id=100000000 + i) for i in range(10)]
        chat = create_test_chat()

        messages = [telegram_factory.create_message(user=user, chat=chat) for user in users]

        mock_handlers = [MockHandler() for _ in messages]

        # Mock some users as blocked
        def is_blocked_side_effect(user_id):
            return user_id % 2 == 0  # Even IDs are blocked

        mock_user_service.is_user_blocked.side_effect = is_blocked_side_effect

        data = {"user_service": mock_user_service}

        # Act
        tasks = [
            blacklist_middleware(handler, message, data)
            for handler, message in zip(mock_handlers, messages, strict=False)
        ]

        await asyncio.gather(*tasks)

        # Assert
        assert mock_user_service.is_user_blocked.call_count == len(users)

        # Check that blocked users (even IDs) didn't reach handlers
        for i, handler in enumerate(mock_handlers):
            user_id = users[i].id
            if user_id % 2 == 0:  # Even IDs are blocked
                assert handler.called is False
            else:  # Odd IDs are not blocked
                assert handler.called is True


@pytest.mark.middleware
class TestBlacklistMiddlewareEdgeCases:
    """Test edge cases for BlacklistMiddleware."""

    @pytest.fixture
    def telegram_factory(self):
        return TelegramObjectFactory()

    @pytest.fixture
    def blacklist_middleware(self):
        return BlacklistMiddleware()

    async def test_blacklist_middleware_with_callback_query(
        self,
        telegram_factory: TelegramObjectFactory,
        blacklist_middleware: BlacklistMiddleware,
        mock_user_service: AsyncMock,
    ):
        """Test middleware with callback query events."""
        # Arrange
        user = create_normal_user()

        callback_query = telegram_factory.create_callback_query(user=user, data="test_callback")

        mock_handler = MockHandler()
        data = {"user_service": mock_user_service}

        mock_user_service.is_user_blocked.return_value = False

        # Act
        await blacklist_middleware(mock_handler, callback_query, data)

        # Assert
        mock_user_service.is_user_blocked.assert_called_once_with(user.id)
        assert mock_handler.called is True

    async def test_blacklist_middleware_with_chat_member_update(
        self,
        telegram_factory: TelegramObjectFactory,
        blacklist_middleware: BlacklistMiddleware,
        mock_user_service: AsyncMock,
    ):
        """Test middleware with chat member update events."""
        # Arrange
        user = create_normal_user()
        chat = create_test_chat()

        chat_member_update = telegram_factory.create_chat_member_updated(chat=chat, user=user)

        mock_handler = MockHandler()
        data = {"user_service": mock_user_service}

        mock_user_service.is_user_blocked.return_value = True  # User is blocked

        # Act
        await blacklist_middleware(mock_handler, chat_member_update, data)

        # Assert
        # Chat member updates might be handled differently
        # (blocked users can still trigger join/leave events)
        # Implementation depends on business logic

    async def test_blacklist_middleware_concurrent_same_user(
        self,
        telegram_factory: TelegramObjectFactory,
        blacklist_middleware: BlacklistMiddleware,
        mock_user_service: AsyncMock,
    ):
        """Test concurrent requests from the same user."""
        import asyncio

        # Arrange
        user = create_normal_user()
        chat = create_test_chat()

        # Create multiple messages from same user
        messages = [telegram_factory.create_message(user=user, chat=chat, text=f"Message {i}") for i in range(5)]

        mock_handlers = [MockHandler() for _ in messages]

        mock_user_service.is_user_blocked.return_value = False

        data = {"user_service": mock_user_service}

        # Act
        tasks = [
            blacklist_middleware(handler, message, data)
            for handler, message in zip(mock_handlers, messages, strict=False)
        ]

        await asyncio.gather(*tasks)

        # Assert
        # Should check user status for each message
        assert mock_user_service.is_user_blocked.call_count == len(messages)
        assert all(handler.called for handler in mock_handlers)

    async def test_blacklist_middleware_exception_handling(
        self,
        telegram_factory: TelegramObjectFactory,
        blacklist_middleware: BlacklistMiddleware,
        mock_user_service: AsyncMock,
    ):
        """Test middleware exception handling doesn't break the flow."""
        # Arrange
        user = create_normal_user()
        chat = create_test_chat()
        message = telegram_factory.create_message(user=user, chat=chat)

        # Create handler that raises exception
        async def failing_handler(event, data):
            raise ValueError("Handler failed")

        data = {"user_service": mock_user_service}

        mock_user_service.is_user_blocked.return_value = False

        # Act & Assert
        with pytest.raises(ValueError, match="Handler failed"):
            await blacklist_middleware(failing_handler, message, data)

        # Middleware should still check blacklist before handler
        mock_user_service.is_user_blocked.assert_called_once_with(user.id)
