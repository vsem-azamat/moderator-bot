"""Tests for event handlers - demonstrating user join/leave simulation."""

from unittest.mock import AsyncMock, patch

import pytest
from app.application.services.user_service import UserService
from app.presentation.telegram.handlers.events import user_joined, user_left

from tests.telegram_helpers import (
    MockBot,
    TelegramEventSimulator,
    TelegramObjectFactory,
    create_admin_user,
    create_normal_user,
    create_test_chat,
)


@pytest.mark.handlers
class TestEventHandlers:
    """Test cases for Telegram event handlers."""

    @pytest.fixture
    def telegram_factory(self):
        return TelegramObjectFactory()

    @pytest.fixture
    def mock_bot(self):
        return MockBot()

    @pytest.fixture
    def mock_user_service(self):
        return AsyncMock(spec=UserService)

    async def test_user_joined_event(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_user_service: AsyncMock
    ):
        """Test handling user joining a chat."""
        # Arrange
        new_user = create_normal_user(id=123456789, username="newuser")
        chat = create_test_chat()
        inviter = create_admin_user()

        # Create user join event
        chat_member_update = telegram_factory.create_chat_member_updated(
            chat=chat,
            user=inviter,
            old_chat_member=telegram_factory.create_user(id=new_user.id),  # Left state
            new_chat_member=new_user,  # Joined state
        )

        mock_user_service.create_or_update_user.return_value = new_user

        # Act
        with patch("app.presentation.telegram.handlers.events.UserService") as mock_service_class:
            mock_service_class.return_value = mock_user_service

            await user_joined(chat_member_update, mock_bot.mock)

        # Assert
        mock_user_service.create_or_update_user.assert_called_once_with(
            user_id=new_user.id,
            username=new_user.username,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
        )

    async def test_user_left_event(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_user_service: AsyncMock
    ):
        """Test handling user leaving a chat."""
        # Arrange
        leaving_user = create_normal_user(id=987654321, username="leaving_user")
        chat = create_test_chat()

        # Create user leave event
        chat_member_update = telegram_factory.create_chat_member_updated(
            chat=chat,
            user=leaving_user,
            old_chat_member=leaving_user,  # Member state
            new_chat_member=telegram_factory.create_user(id=leaving_user.id),  # Left state
        )

        # Act
        with patch("app.presentation.telegram.handlers.events.UserService") as mock_service_class:
            mock_service_class.return_value = mock_user_service

            await user_left(chat_member_update, mock_bot.mock)

        # Assert - Verify appropriate logging or cleanup actions
        # This depends on your actual user_left handler implementation
        mock_service_class.assert_called_once()

    async def test_multiple_users_joining_simultaneously(
        self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot, mock_user_service: AsyncMock
    ):
        """Test multiple users joining simultaneously."""
        import asyncio

        # Arrange
        chat = create_test_chat()
        new_users = [
            create_normal_user(id=100000001, username="user1"),
            create_normal_user(id=100000002, username="user2"),
            create_normal_user(id=100000003, username="user3"),
        ]

        mock_user_service.create_or_update_user.return_value = None

        # Create join events for all users
        join_events = []
        for user in new_users:
            event = telegram_factory.create_chat_member_updated(
                chat=chat, user=user, old_chat_member=telegram_factory.create_user(id=user.id), new_chat_member=user
            )
            join_events.append(event)

        # Act - Process all joins concurrently
        async def handle_join(event):
            with patch("app.presentation.telegram.handlers.events.UserService") as mock_service_class:
                mock_service_class.return_value = mock_user_service
                await user_joined(event, mock_bot.mock)

        await asyncio.gather(*[handle_join(event) for event in join_events])

        # Assert
        assert mock_user_service.create_or_update_user.call_count == len(new_users)


@pytest.mark.handlers
class TestEventSimulatorUsage:
    """Demonstrate using TelegramEventSimulator for complex scenarios."""

    @pytest.fixture
    async def event_simulator(self):
        from tests.telegram_helpers import HandlerTestContext

        context = HandlerTestContext()
        return TelegramEventSimulator(context)

    async def test_complete_user_workflow_simulation(
        self, event_simulator: TelegramEventSimulator, mock_user_service: AsyncMock
    ):
        """Test complete workflow: user joins -> sends message -> gets moderated -> leaves."""
        # 1. Simulate new user joining
        new_user = create_normal_user(id=555555555, username="troublemaker")
        chat = create_test_chat()

        join_event = await event_simulator.simulate_user_join(user=new_user, chat=chat)

        assert join_event.new_chat_member.user.id == new_user.id

        # 2. Simulate user sending a problematic message
        event_simulator.factory.create_message(user=new_user, chat=chat, text="🚨 SPAM MESSAGE 🚨")

        # 3. Simulate admin muting the user
        admin = create_admin_user()
        mute_command = await event_simulator.simulate_moderation_action(
            action="mute", admin=admin, target_user=new_user, chat=chat, args="10"
        )

        assert "mute" in mute_command.text
        assert mute_command.reply_to_message.from_user.id == new_user.id

        # 4. Simulate user leaving after being muted
        leave_event = await event_simulator.simulate_user_leave(user=new_user, chat=chat)

        assert leave_event.old_chat_member.user.id == new_user.id

    async def test_admin_interaction_simulation(self, event_simulator: TelegramEventSimulator):
        """Test admin commands and button interactions."""
        admin = create_admin_user()
        target_user = create_normal_user()
        chat = create_test_chat()

        # 1. Simulate ban command
        await event_simulator.simulate_moderation_action(
            action="ban", admin=admin, target_user=target_user, chat=chat, args="delete"
        )

        # 2. Simulate clicking unban button (from blacklist menu)
        unban_callback = await event_simulator.simulate_button_click(
            callback_data=f"unban:{target_user.id}", user=admin
        )

        assert unban_callback.data == f"unban:{target_user.id}"
        assert unban_callback.from_user.id == admin.id

    async def test_welcome_message_scenario(
        self, event_simulator: TelegramEventSimulator, mock_user_service: AsyncMock
    ):
        """Test welcome message flow for new users."""
        # Arrange
        new_user = create_normal_user(id=777888999, username="newcomer")
        chat = create_test_chat()

        # Simulate user joining
        join_event = await event_simulator.simulate_user_join(user=new_user, chat=chat)

        # Mock welcome service
        mock_user_service.create_or_update_user.return_value = new_user

        # Act - Simulate welcome handler processing
        with patch("app.presentation.telegram.handlers.events.UserService") as mock_service_class:
            mock_service_class.return_value = mock_user_service

            # This would trigger your welcome message handler
            await user_joined(join_event, event_simulator.context.bot.mock)

        # Assert
        mock_user_service.create_or_update_user.assert_called_once()
        # You can add more assertions based on your welcome message logic
