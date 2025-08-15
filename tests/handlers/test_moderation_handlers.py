"""Tests for moderation handlers."""

from unittest.mock import AsyncMock, patch

import pytest
from app.application.services.moderation_service import ModerationService
from app.application.services.user_service import UserService
from app.presentation.telegram.handlers.moderation import ban_user, mute_user, unban_user, unmute_user

from tests.telegram_helpers import (
    MockBot,
    TelegramObjectFactory,
    create_admin_user,
    create_normal_user,
    create_test_chat,
)


@pytest.mark.handlers
class TestModerationHandlers:
    """Test cases for moderation handlers."""

    @pytest.fixture
    def telegram_factory(self):
        return TelegramObjectFactory()

    @pytest.fixture
    def mock_bot(self):
        return MockBot()

    @pytest.fixture
    def mock_moderation_service(self):
        return AsyncMock(spec=ModerationService)

    @pytest.fixture
    def mock_user_service(self):
        return AsyncMock(spec=UserService)

    async def test_mute_user_default_duration(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_moderation_service: AsyncMock
    ):
        """Test muting user with default duration (5 minutes)."""
        # Arrange
        admin_user = create_admin_user()
        target_user = create_normal_user(id=777777777, username="spammer")
        chat = create_test_chat()

        # Create mute command message (reply to target user)
        reply_message = telegram_factory.create_message(user=target_user, chat=chat)
        command_message = telegram_factory.create_command_message(
            command="mute", user=admin_user, chat=chat, reply_to_message=reply_message
        )

        # Mock successful moderation
        mock_moderation_service.mute_user.return_value = None

        # Act
        with patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_service_class:
            mock_service_class.return_value = mock_moderation_service

            await mute_user(command_message, mock_bot.mock)

        # Assert
        mock_moderation_service.mute_user.assert_called_once()
        call_args = mock_moderation_service.mute_user.call_args

        assert call_args[1]["admin_id"] == admin_user.id
        assert call_args[1]["user_id"] == target_user.id
        assert call_args[1]["chat_id"] == chat.id
        assert call_args[1]["duration"].minutes == 5  # Default duration

        command_message.answer.assert_called_once()
        answer_text = command_message.answer.call_args[0][0]
        assert "заглушен" in answer_text.lower() or "muted" in answer_text.lower()

    async def test_mute_user_custom_duration(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_moderation_service: AsyncMock
    ):
        """Test muting user with custom duration."""
        # Arrange
        admin_user = create_admin_user()
        target_user = create_normal_user()
        chat = create_test_chat()

        reply_message = telegram_factory.create_message(user=target_user, chat=chat)
        command_message = telegram_factory.create_command_message(
            command="mute",
            args="10",  # 10 minutes
            user=admin_user,
            chat=chat,
            reply_to_message=reply_message,
        )

        mock_moderation_service.mute_user.return_value = None

        # Act
        with patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_service_class:
            mock_service_class.return_value = mock_moderation_service

            await mute_user(command_message, mock_bot.mock)

        # Assert
        call_args = mock_moderation_service.mute_user.call_args
        assert call_args[1]["duration"].minutes == 10

    async def test_mute_user_invalid_duration(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_moderation_service: AsyncMock
    ):
        """Test mute command with invalid duration argument."""
        # Arrange
        admin_user = create_admin_user()
        target_user = create_normal_user()
        chat = create_test_chat()

        reply_message = telegram_factory.create_message(user=target_user, chat=chat)
        command_message = telegram_factory.create_command_message(
            command="mute",
            args="invalid",  # Invalid duration
            user=admin_user,
            chat=chat,
            reply_to_message=reply_message,
        )

        # Act
        with patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_service_class:
            mock_service_class.return_value = mock_moderation_service

            await mute_user(command_message, mock_bot.mock)

        # Assert - Should use default duration when parsing fails
        call_args = mock_moderation_service.mute_user.call_args
        assert call_args[1]["duration"].minutes == 5  # Default fallback

    async def test_mute_user_telegram_error(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_moderation_service: AsyncMock
    ):
        """Test mute command when Telegram API fails."""
        # Arrange
        admin_user = create_admin_user()
        target_user = create_normal_user()
        chat = create_test_chat()

        reply_message = telegram_factory.create_message(user=target_user, chat=chat)
        command_message = telegram_factory.create_command_message(
            command="mute", user=admin_user, chat=chat, reply_to_message=reply_message
        )

        # Mock Telegram API error
        from app.domain.exceptions import TelegramApiException

        mock_moderation_service.mute_user.side_effect = TelegramApiException("mute_user", "User not found")

        # Act
        with patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_service_class:
            mock_service_class.return_value = mock_moderation_service

            await mute_user(command_message, mock_bot.mock)

        # Assert - Should handle error gracefully
        command_message.answer.assert_called_once()
        answer_text = command_message.answer.call_args[0][0]
        assert "ошибк" in answer_text.lower() or "error" in answer_text.lower()

    async def test_unmute_user_success(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_moderation_service: AsyncMock
    ):
        """Test successfully unmuting a user."""
        # Arrange
        admin_user = create_admin_user()
        target_user = create_normal_user()
        chat = create_test_chat()

        reply_message = telegram_factory.create_message(user=target_user, chat=chat)
        command_message = telegram_factory.create_command_message(
            command="unmute", user=admin_user, chat=chat, reply_to_message=reply_message
        )

        mock_moderation_service.unmute_user.return_value = None

        # Act
        with patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_service_class:
            mock_service_class.return_value = mock_moderation_service

            await unmute_user(command_message, mock_bot.mock)

        # Assert
        mock_moderation_service.unmute_user.assert_called_once_with(
            admin_id=admin_user.id, user_id=target_user.id, chat_id=chat.id
        )

        command_message.answer.assert_called_once()
        answer_text = command_message.answer.call_args[0][0]
        assert "разглушен" in answer_text.lower() or "unmuted" in answer_text.lower()

    async def test_ban_user_success(
        self,
        telegram_factory: TelegramObjectFactory,
        mock_bot: MockBot,
        mock_moderation_service: AsyncMock,
        mock_user_service: AsyncMock,
    ):
        """Test successfully banning a user."""
        # Arrange
        admin_user = create_admin_user()
        target_user = create_normal_user()
        chat = create_test_chat()

        reply_message = telegram_factory.create_message(user=target_user, chat=chat)
        command_message = telegram_factory.create_command_message(
            command="ban", user=admin_user, chat=chat, reply_to_message=reply_message
        )

        mock_moderation_service.ban_user.return_value = None
        mock_user_service.block_user.return_value = None

        # Act
        with (
            patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_mod_class,
            patch("app.presentation.telegram.handlers.moderation.UserService") as mock_user_class,
        ):
            mock_mod_class.return_value = mock_moderation_service
            mock_user_class.return_value = mock_user_service

            await ban_user(command_message, mock_bot.mock)

        # Assert
        mock_moderation_service.ban_user.assert_called_once()
        mock_user_service.block_user.assert_called_once_with(target_user.id)

        command_message.answer.assert_called_once()
        answer_text = command_message.answer.call_args[0][0]
        assert "заблокирован" in answer_text.lower() or "banned" in answer_text.lower()

    async def test_ban_user_with_message_deletion(
        self,
        telegram_factory: TelegramObjectFactory,
        mock_bot: MockBot,
        mock_moderation_service: AsyncMock,
        mock_user_service: AsyncMock,
    ):
        """Test banning user with message deletion."""
        # Arrange
        admin_user = create_admin_user()
        target_user = create_normal_user()
        chat = create_test_chat()

        reply_message = telegram_factory.create_message(user=target_user, chat=chat)
        command_message = telegram_factory.create_command_message(
            command="ban",
            args="delete",  # Delete messages flag
            user=admin_user,
            chat=chat,
            reply_to_message=reply_message,
        )

        mock_moderation_service.ban_user.return_value = None
        mock_user_service.block_user.return_value = None

        # Act
        with (
            patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_mod_class,
            patch("app.presentation.telegram.handlers.moderation.UserService") as mock_user_class,
        ):
            mock_mod_class.return_value = mock_moderation_service
            mock_user_class.return_value = mock_user_service

            await ban_user(command_message, mock_bot.mock)

        # Assert
        call_args = mock_moderation_service.ban_user.call_args
        assert call_args[1]["revoke_messages"] is True

    async def test_unban_user_success(
        self,
        telegram_factory: TelegramObjectFactory,
        mock_bot: MockBot,
        mock_moderation_service: AsyncMock,
        mock_user_service: AsyncMock,
    ):
        """Test successfully unbanning a user."""
        # Arrange
        admin_user = create_admin_user()
        target_user = create_normal_user()
        chat = create_test_chat()

        reply_message = telegram_factory.create_message(user=target_user, chat=chat)
        command_message = telegram_factory.create_command_message(
            command="unban", user=admin_user, chat=chat, reply_to_message=reply_message
        )

        mock_moderation_service.unban_user.return_value = None
        mock_user_service.unblock_user.return_value = None

        # Act
        with (
            patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_mod_class,
            patch("app.presentation.telegram.handlers.moderation.UserService") as mock_user_class,
        ):
            mock_mod_class.return_value = mock_moderation_service
            mock_user_class.return_value = mock_user_service

            await unban_user(command_message, mock_bot.mock)

        # Assert
        mock_moderation_service.unban_user.assert_called_once()
        mock_user_service.unblock_user.assert_called_once_with(target_user.id)

        command_message.answer.assert_called_once()
        answer_text = command_message.answer.call_args[0][0]
        assert "разблокирован" in answer_text.lower() or "unbanned" in answer_text.lower()


@pytest.mark.handlers
class TestModerationHandlerEdgeCases:
    """Test edge cases for moderation handlers."""

    @pytest.fixture
    def telegram_factory(self):
        return TelegramObjectFactory()

    async def test_moderation_command_no_reply(self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot):
        """Test moderation command without reply to target user."""
        # Arrange
        admin_user = create_admin_user()
        chat = create_test_chat()

        command_message = telegram_factory.create_command_message(
            command="mute",
            user=admin_user,
            chat=chat,
            reply_to_message=None,  # No reply
        )

        # Act & Assert
        with pytest.raises(AttributeError):
            await mute_user(command_message, mock_bot.mock)

    async def test_moderation_self_target(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_moderation_service: AsyncMock
    ):
        """Test admin trying to moderate themselves."""
        # Arrange
        admin_user = create_admin_user()
        chat = create_test_chat()

        # Admin replies to their own message
        reply_message = telegram_factory.create_message(user=admin_user, chat=chat)
        command_message = telegram_factory.create_command_message(
            command="mute", user=admin_user, chat=chat, reply_to_message=reply_message
        )

        # Mock service to raise appropriate error
        from app.domain.exceptions import InvalidModerationTargetException

        mock_moderation_service.mute_user.side_effect = InvalidModerationTargetException("Cannot moderate yourself")

        # Act
        with patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_service_class:
            mock_service_class.return_value = mock_moderation_service

            await mute_user(command_message, mock_bot.mock)

        # Assert
        command_message.answer.assert_called_once()
        answer_text = command_message.answer.call_args[0][0]
        assert "нельзя" in answer_text.lower() or "cannot" in answer_text.lower()

    async def test_moderation_extreme_duration(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_moderation_service: AsyncMock
    ):
        """Test mute with extreme duration values."""
        # Arrange
        admin_user = create_admin_user()
        target_user = create_normal_user()
        chat = create_test_chat()

        reply_message = telegram_factory.create_message(user=target_user, chat=chat)
        command_message = telegram_factory.create_command_message(
            command="mute",
            args="999999",  # Very large duration
            user=admin_user,
            chat=chat,
            reply_to_message=reply_message,
        )

        # Mock duration validation error
        mock_moderation_service.mute_user.side_effect = ValueError("Mute duration cannot exceed 1 year")

        # Act
        with patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_service_class:
            mock_service_class.return_value = mock_moderation_service

            await mute_user(command_message, mock_bot.mock)

        # Assert
        command_message.answer.assert_called_once()
        answer_text = command_message.answer.call_args[0][0]
        assert "неверн" in answer_text.lower() or "invalid" in answer_text.lower()

    async def test_concurrent_moderation_actions(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_moderation_service: AsyncMock
    ):
        """Test concurrent moderation actions on different users."""
        import asyncio

        # Arrange
        admin_user = create_admin_user()
        target_users = [
            create_normal_user(id=777777771, username="user1"),
            create_normal_user(id=777777772, username="user2"),
            create_normal_user(id=777777773, username="user3"),
        ]
        chat = create_test_chat()

        messages = []
        for target_user in target_users:
            reply_message = telegram_factory.create_message(user=target_user, chat=chat)
            command_message = telegram_factory.create_command_message(
                command="mute", user=admin_user, chat=chat, reply_to_message=reply_message
            )
            messages.append(command_message)

        mock_moderation_service.mute_user.return_value = None

        # Act
        async def mute_task(message):
            with patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_service_class:
                mock_service_class.return_value = mock_moderation_service
                await mute_user(message, mock_bot.mock)

        tasks = [mute_task(msg) for msg in messages]
        await asyncio.gather(*tasks)

        # Assert
        assert mock_moderation_service.mute_user.call_count == len(target_users)

    async def test_moderation_permission_error(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_moderation_service: AsyncMock
    ):
        """Test moderation when bot lacks permissions."""
        # Arrange
        admin_user = create_admin_user()
        target_user = create_normal_user()
        chat = create_test_chat()

        reply_message = telegram_factory.create_message(user=target_user, chat=chat)
        command_message = telegram_factory.create_command_message(
            command="mute", user=admin_user, chat=chat, reply_to_message=reply_message
        )

        # Mock permission error
        from app.domain.exceptions import TelegramApiException

        mock_moderation_service.mute_user.side_effect = TelegramApiException(
            "mute_user", "Not enough rights to restrict/unrestrict chat member"
        )

        # Act
        with patch("app.presentation.telegram.handlers.moderation.ModerationService") as mock_service_class:
            mock_service_class.return_value = mock_moderation_service

            await mute_user(command_message, mock_bot.mock)

        # Assert
        command_message.answer.assert_called_once()
        answer_text = command_message.answer.call_args[0][0]
        assert "права" in answer_text.lower() or "permission" in answer_text.lower()
