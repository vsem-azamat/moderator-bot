"""Tests for application services."""

from unittest.mock import AsyncMock, patch

import pytest
from app.application.services import buttons, report


@pytest.mark.unit
class TestButtonsService:
    """Test buttons service."""

    async def test_get_contacts_buttons(self):
        """Test getting contacts buttons."""
        # Act
        builder = await buttons.get_contacts_buttons()

        # Assert
        keyboard = builder.as_markup()
        assert len(keyboard.inline_keyboard) == 2  # Two rows (2 buttons, adjust(1))

        # Check first button (Dev)
        dev_button = keyboard.inline_keyboard[0][0]
        assert dev_button.text == "Dev"
        assert dev_button.url == "https://t.me/vsem_azamat"

        # Check second button (GitHub)
        github_button = keyboard.inline_keyboard[1][0]
        assert github_button.text == "GitHub"
        assert github_button.url == "https://github.com/vsem-azamat/moderator-bot"

    async def test_get_chat_buttons_empty(self):
        """Test getting chat buttons when no chats exist."""
        # Arrange
        mock_db = AsyncMock()

        with patch("app.application.services.buttons.ChatLinkRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_chat_links.return_value = []
            mock_repo_class.return_value = mock_repo

            # Act
            builder = await buttons.get_chat_buttons(mock_db)

            # Assert
            keyboard = builder.as_markup()
            assert len(keyboard.inline_keyboard) == 0

    async def test_get_chat_buttons_with_chats(self):
        """Test getting chat buttons with existing chats."""
        # Arrange
        mock_db = AsyncMock()
        mock_chat1 = AsyncMock()
        mock_chat1.text = "Chat 1"
        mock_chat1.link = "https://t.me/chat1"

        mock_chat2 = AsyncMock()
        mock_chat2.text = "Chat 2"
        mock_chat2.link = "https://t.me/chat2"

        with patch("app.application.services.buttons.ChatLinkRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_chat_links.return_value = [mock_chat1, mock_chat2]
            mock_repo_class.return_value = mock_repo

            # Act
            builder = await buttons.get_chat_buttons(mock_db)

            # Assert
            keyboard = builder.as_markup()
            assert len(keyboard.inline_keyboard) == 1  # One row with 2 buttons (adjust(2))
            assert len(keyboard.inline_keyboard[0]) == 2  # Two buttons in the row

            # Check buttons
            button1 = keyboard.inline_keyboard[0][0]
            assert button1.text == "Chat 1"
            assert button1.url == "https://t.me/chat1"

            button2 = keyboard.inline_keyboard[0][1]
            assert button2.text == "Chat 2"
            assert button2.url == "https://t.me/chat2"


@pytest.mark.unit
class TestReportService:
    """Test report service."""

    @pytest.fixture
    def mock_bot(self):
        return AsyncMock()

    @pytest.fixture
    def mock_reporter(self):
        user = AsyncMock()
        user.id = 123456789
        user.username = "reporter"
        user.first_name = "John"
        return user

    @pytest.fixture
    def mock_reported(self):
        user = AsyncMock()
        user.id = 987654321
        user.username = "reported"
        user.first_name = "Jane"
        return user

    @pytest.fixture
    def mock_message(self):
        message = AsyncMock()
        message.text = "This is a reported message"
        message.message_id = 456
        return message

    async def test_report_to_moderators(self, mock_bot, mock_reporter, mock_reported, mock_message):
        """Test reporting to moderators."""
        with (
            patch("app.application.services.report.other.get_chat_mention") as mock_chat_mention,
            patch("app.application.services.report.other.get_message_mention") as mock_msg_mention,
            patch("app.application.services.report.other.get_user_mention") as mock_user_mention,
            patch("app.application.services.report.settings") as mock_settings,
        ):
            # Configure mocks
            mock_chat_mention.return_value = "Chat Name"
            mock_msg_mention.return_value = "Message Link"
            mock_user_mention.side_effect = lambda user: f"@{user.username}"
            mock_settings.admin.default_report_chat_id = -1001234567890

            # Act
            await report.report_to_moderators(mock_bot, mock_reporter, mock_reported, mock_message)

            # Assert
            mock_bot.send_message.assert_called_once()
            call_args = mock_bot.send_message.call_args

            # Check chat_id
            assert call_args[1]["chat_id"] == -1001234567890

            # Check message content
            message_text = call_args[1]["text"]
            assert "🚨" in message_text
            assert "@reporter" in message_text
            assert "@reported" in message_text
            assert "Chat Name" in message_text
            assert "Message Link" in message_text
            assert "This is a reported message" in message_text

    async def test_report_to_moderators_calls_utility_functions(
        self, mock_bot, mock_reporter, mock_reported, mock_message
    ):
        """Test that report function calls all required utility functions."""
        with (
            patch("app.application.services.report.other.get_chat_mention") as mock_chat_mention,
            patch("app.application.services.report.other.get_message_mention") as mock_msg_mention,
            patch("app.application.services.report.other.get_user_mention") as mock_user_mention,
            patch("app.application.services.report.settings") as mock_settings,
        ):
            # Configure mocks
            mock_chat_mention.return_value = "Chat"
            mock_msg_mention.return_value = "Message"
            mock_user_mention.return_value = "User"
            mock_settings.admin.default_report_chat_id = -1001234567890

            # Act
            await report.report_to_moderators(mock_bot, mock_reporter, mock_reported, mock_message)

            # Assert all utility functions were called
            mock_chat_mention.assert_called_once_with(mock_message)
            mock_msg_mention.assert_called_once_with(mock_message)
            assert mock_user_mention.call_count == 2  # Called for both reporter and reported
            mock_user_mention.assert_any_call(mock_reporter)
            mock_user_mention.assert_any_call(mock_reported)


@pytest.mark.unit
class TestApplicationServiceIntegration:
    """Integration tests for application services."""

    async def test_buttons_and_report_services_independent(self):
        """Test that buttons and report services work independently."""
        # Test that we can use both services without interference

        # Test buttons service
        contacts_builder = await buttons.get_contacts_buttons()
        assert contacts_builder is not None

        # Test report service with mocks
        mock_bot = AsyncMock()
        mock_reporter = AsyncMock()
        mock_reported = AsyncMock()
        mock_message = AsyncMock()
        mock_message.text = "Test message"

        with (
            patch("app.application.services.report.other.get_chat_mention") as mock_chat_mention,
            patch("app.application.services.report.other.get_message_mention") as mock_msg_mention,
            patch("app.application.services.report.other.get_user_mention") as mock_user_mention,
            patch("app.application.services.report.settings") as mock_settings,
        ):
            mock_chat_mention.return_value = "Chat"
            mock_msg_mention.return_value = "Message"
            mock_user_mention.return_value = "User"
            mock_settings.admin.default_report_chat_id = -1001234567890

            # This should not raise any exceptions
            await report.report_to_moderators(mock_bot, mock_reporter, mock_reported, mock_message)

        # Both services should work without interference
        contacts_builder2 = await buttons.get_contacts_buttons()
        assert contacts_builder2 is not None
