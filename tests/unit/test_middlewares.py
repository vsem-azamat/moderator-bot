"""Tests for telegram middlewares."""

from unittest.mock import AsyncMock

import pytest
from aiogram import types
from app.presentation.telegram.middlewares.chat_type import ChatTypeMiddleware


@pytest.mark.unit
class TestChatTypeMiddleware:
    """Test ChatTypeMiddleware."""

    @pytest.fixture
    def mock_handler(self):
        """Mock handler for middleware testing."""
        handler = AsyncMock()
        handler.return_value = "handler_result"
        return handler

    @pytest.fixture
    def mock_group_message(self):
        """Mock group message."""
        message = AsyncMock(spec=types.Message)
        message.chat = AsyncMock()
        message.chat.type = "group"
        return message

    @pytest.fixture
    def mock_supergroup_message(self):
        """Mock supergroup message."""
        message = AsyncMock(spec=types.Message)
        message.chat = AsyncMock()
        message.chat.type = "supergroup"
        return message

    @pytest.fixture
    def mock_private_message(self):
        """Mock private message."""
        message = AsyncMock(spec=types.Message)
        message.chat = AsyncMock()
        message.chat.type = "private"
        return message

    async def test_single_chat_type_match(self, mock_handler, mock_group_message):
        """Test middleware with single chat type that matches."""
        # Arrange
        middleware = ChatTypeMiddleware("group")
        data = {}

        # Act
        result = await middleware(mock_handler, mock_group_message, data)

        # Assert
        assert result == "handler_result"
        mock_handler.assert_called_once_with(mock_group_message, data)

    async def test_single_chat_type_no_match(self, mock_handler, mock_private_message):
        """Test middleware with single chat type that doesn't match."""
        # Arrange
        middleware = ChatTypeMiddleware("group")
        data = {}

        # Act
        result = await middleware(mock_handler, mock_private_message, data)

        # Assert
        assert result is None
        mock_handler.assert_not_called()

    async def test_multiple_chat_types_match(self, mock_handler, mock_supergroup_message):
        """Test middleware with multiple chat types that match."""
        # Arrange
        middleware = ChatTypeMiddleware(["group", "supergroup"])
        data = {}

        # Act
        result = await middleware(mock_handler, mock_supergroup_message, data)

        # Assert
        assert result == "handler_result"
        mock_handler.assert_called_once_with(mock_supergroup_message, data)

    async def test_multiple_chat_types_no_match(self, mock_handler, mock_private_message):
        """Test middleware with multiple chat types that don't match."""
        # Arrange
        middleware = ChatTypeMiddleware(["group", "supergroup"])
        data = {}

        # Act
        result = await middleware(mock_handler, mock_private_message, data)

        # Assert
        assert result is None
        mock_handler.assert_not_called()

    async def test_non_message_event(self, mock_handler):
        """Test middleware with non-message event."""
        # Arrange
        middleware = ChatTypeMiddleware("group")
        callback_query = AsyncMock(spec=types.CallbackQuery)
        data = {}

        # Act
        result = await middleware(mock_handler, callback_query, data)

        # Assert
        assert result is None
        mock_handler.assert_not_called()

    async def test_empty_chat_types_list(self, mock_handler, mock_group_message):
        """Test middleware with empty chat types list."""
        # Arrange
        middleware = ChatTypeMiddleware([])
        data = {}

        # Act
        result = await middleware(mock_handler, mock_group_message, data)

        # Assert
        assert result is None
        mock_handler.assert_not_called()

    async def test_data_passed_through(self, mock_handler, mock_group_message):
        """Test that data is passed through to handler."""
        # Arrange
        middleware = ChatTypeMiddleware("group")
        data = {"test_key": "test_value", "another_key": 123}

        # Act
        result = await middleware(mock_handler, mock_group_message, data)

        # Assert
        assert result == "handler_result"
        mock_handler.assert_called_once_with(mock_group_message, data)

    async def test_handler_exception_propagated(self, mock_group_message):
        """Test that handler exceptions are propagated."""
        # Arrange
        middleware = ChatTypeMiddleware("group")
        mock_handler = AsyncMock()
        mock_handler.side_effect = ValueError("Handler error")
        data = {}

        # Act & Assert
        with pytest.raises(ValueError, match="Handler error"):
            await middleware(mock_handler, mock_group_message, data)

    async def test_case_sensitive_chat_type(self, mock_handler):
        """Test that chat type matching is case sensitive."""
        # Arrange
        middleware = ChatTypeMiddleware("GROUP")  # Uppercase
        message = AsyncMock(spec=types.Message)
        message.chat = AsyncMock()
        message.chat.type = "group"  # Lowercase
        data = {}

        # Act
        result = await middleware(mock_handler, message, data)

        # Assert
        assert result is None
        mock_handler.assert_not_called()

    async def test_middleware_with_all_chat_types(self, mock_handler):
        """Test middleware configured for all common chat types."""
        # Arrange
        middleware = ChatTypeMiddleware(["private", "group", "supergroup", "channel"])
        data = {}

        # Test private chat
        private_msg = AsyncMock(spec=types.Message)
        private_msg.chat = AsyncMock()
        private_msg.chat.type = "private"

        result = await middleware(mock_handler, private_msg, data)
        assert result == "handler_result"

        # Test group chat
        group_msg = AsyncMock(spec=types.Message)
        group_msg.chat = AsyncMock()
        group_msg.chat.type = "group"

        mock_handler.reset_mock()
        result = await middleware(mock_handler, group_msg, data)
        assert result == "handler_result"

        # Test supergroup chat
        supergroup_msg = AsyncMock(spec=types.Message)
        supergroup_msg.chat = AsyncMock()
        supergroup_msg.chat.type = "supergroup"

        mock_handler.reset_mock()
        result = await middleware(mock_handler, supergroup_msg, data)
        assert result == "handler_result"

    async def test_middleware_initialization(self):
        """Test middleware initialization with different parameter types."""
        # Test with string
        middleware_str = ChatTypeMiddleware("group")
        assert middleware_str.chat_types == "group"

        # Test with list
        middleware_list = ChatTypeMiddleware(["group", "supergroup"])
        assert middleware_list.chat_types == ["group", "supergroup"]

        # Test with single-item list
        middleware_single_list = ChatTypeMiddleware(["private"])
        assert middleware_single_list.chat_types == ["private"]
