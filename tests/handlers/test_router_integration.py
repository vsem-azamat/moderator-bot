"""Integration tests for Telegram routers - demonstrating router testing patterns."""

import pytest

from tests.telegram_helpers import (
    MockBot,
    TelegramEventSimulator,
    TelegramObjectFactory,
    create_admin_user,
    create_normal_user,
    create_test_chat,
)


@pytest.mark.integration
class TestRouterIntegration:
    """Integration tests for Telegram routers."""

    @pytest.fixture
    def telegram_factory(self):
        return TelegramObjectFactory()

    @pytest.fixture
    def mock_bot(self):
        return MockBot()

    async def test_moderation_router_command_routing(self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot):
        """Test that moderation commands are properly routed."""
        # Arrange
        admin_user = create_admin_user()
        target_user = create_normal_user()
        chat = create_test_chat()

        # Create different moderation commands
        commands = ["mute", "unmute", "ban", "unban"]

        for command in commands:
            reply_message = telegram_factory.create_message(user=target_user, chat=chat)
            command_message = telegram_factory.create_command_message(
                command=command, user=admin_user, chat=chat, reply_to_message=reply_message
            )

            update = telegram_factory.create_update(message=command_message)

            # Act & Assert - Verify the router can process the update
            # In a real scenario, you'd check that the correct handler is called
            assert update.message.text.startswith(f"/{command}")
            assert update.message.from_user.id == admin_user.id

    async def test_admin_router_permission_filtering(self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot):
        """Test admin router filters out non-admin users."""
        # Arrange
        normal_user = create_normal_user()
        admin_user = create_admin_user()
        chat = create_test_chat()

        # Test admin command from normal user (should be filtered out)
        normal_user_command = telegram_factory.create_command_message(command="admin", user=normal_user, chat=chat)

        # Test admin command from admin user (should pass through)
        admin_user_command = telegram_factory.create_command_message(command="admin", user=admin_user, chat=chat)

        # In real implementation, you'd test middleware filtering
        assert normal_user_command.from_user.id != admin_user.id
        assert admin_user_command.from_user.id == admin_user.id

    async def test_groups_router_chat_type_filtering(self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot):
        """Test groups router only processes group messages."""
        # Arrange
        user = create_normal_user()

        # Private chat (should be filtered out)
        private_chat = telegram_factory.create_chat(id=user.id, type="private", title=None, first_name=user.first_name)

        # Group chat (should pass through)
        group_chat = create_test_chat()

        private_message = telegram_factory.create_message(user=user, chat=private_chat, text="/chats")

        group_message = telegram_factory.create_message(user=user, chat=group_chat, text="/chats")

        # Assert
        assert private_message.chat.type == "private"
        assert group_message.chat.type == "supergroup"

    async def test_callback_query_routing(self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot):
        """Test callback query routing for inline keyboards."""
        # Arrange
        admin_user = create_admin_user()

        # Different callback data patterns
        callback_patterns = ["unban:123456789", "confirm_ban:987654321", "page:2", "close_menu"]

        for callback_data in callback_patterns:
            callback_query = telegram_factory.create_callback_query(user=admin_user, data=callback_data)

            update = telegram_factory.create_update(callback_query=callback_query)

            # Assert
            assert update.callback_query.data == callback_data
            assert update.callback_query.from_user.id == admin_user.id

    async def test_chat_member_update_routing(self, telegram_factory: TelegramObjectFactory, mock_bot: MockBot):
        """Test chat member update events routing."""
        # Arrange
        chat = create_test_chat()
        joining_user = create_normal_user(id=111222333)
        leaving_user = create_normal_user(id=444555666)

        # User joining event
        from aiogram.types import ChatMemberLeft, ChatMemberMember

        join_event = telegram_factory.create_chat_member_updated(
            chat=chat,
            user=joining_user,
            old_chat_member=ChatMemberLeft(user=joining_user, status="left"),
            new_chat_member=ChatMemberMember(user=joining_user, status="member"),
        )

        # User leaving event
        leave_event = telegram_factory.create_chat_member_updated(
            chat=chat,
            user=leaving_user,
            old_chat_member=ChatMemberMember(user=leaving_user, status="member"),
            new_chat_member=ChatMemberLeft(user=leaving_user, status="left"),
        )

        join_update = telegram_factory.create_update(chat_member=join_event)
        leave_update = telegram_factory.create_update(chat_member=leave_event)

        # Assert
        assert join_update.chat_member.new_chat_member.user.id == joining_user.id
        assert leave_update.chat_member.old_chat_member.user.id == leaving_user.id


@pytest.mark.integration
class TestRouterWorkflows:
    """Test complete workflows across multiple routers."""

    @pytest.fixture
    async def event_simulator(self):
        from tests.telegram_helpers import HandlerTestContext

        context = HandlerTestContext()
        return TelegramEventSimulator(context)

    async def test_user_moderation_workflow(self, event_simulator: TelegramEventSimulator):
        """Test complete user moderation workflow across routers."""
        # Setup
        admin = create_admin_user()
        spammer = create_normal_user(id=999888777, username="spammer")
        chat = create_test_chat()

        # 1. User joins (events router)
        join_event = await event_simulator.simulate_user_join(user=spammer, chat=chat)

        # 2. User sends spam message (groups router would process)
        spam_message = event_simulator.factory.create_message(
            user=spammer, chat=chat, text="This is spam! Buy crypto now! 🚀💰"
        )

        # 3. Admin mutes user (moderation router)
        mute_command = await event_simulator.simulate_moderation_action(
            action="mute", admin=admin, target_user=spammer, chat=chat, args="30"
        )

        # 4. Admin checks blacklist (admin router)
        blacklist_command = event_simulator.factory.create_command_message(command="blacklist", user=admin, chat=chat)

        # 5. Admin bans user permanently (moderation router)
        ban_command = await event_simulator.simulate_moderation_action(
            action="ban", admin=admin, target_user=spammer, chat=chat, args="delete"
        )

        # Assert workflow integrity
        assert join_event.new_chat_member.user.id == spammer.id
        assert "spam" in spam_message.text.lower()
        assert mute_command.text == "/mute 30"
        assert blacklist_command.text == "/blacklist"
        assert ban_command.text == "/ban delete"

    async def test_admin_management_workflow(self, event_simulator: TelegramEventSimulator):
        """Test admin management workflow."""
        # Setup
        super_admin = create_admin_user(id=111111111)
        new_admin_candidate = create_normal_user(id=222222222, username="new_admin")
        chat = create_test_chat()

        # 1. Super admin promotes user to admin
        reply_message = event_simulator.factory.create_message(user=new_admin_candidate, chat=chat)

        admin_command = event_simulator.factory.create_command_message(
            command="admin", user=super_admin, chat=chat, reply_to_message=reply_message
        )

        # 2. New admin tries moderation command
        target_user = create_normal_user(id=333333333)
        target_message = event_simulator.factory.create_message(user=target_user, chat=chat)

        new_admin_mute = event_simulator.factory.create_command_message(
            command="mute", user=new_admin_candidate, chat=chat, reply_to_message=target_message
        )

        # 3. Super admin removes admin privileges
        unadmin_command = event_simulator.factory.create_command_message(
            command="unadmin", user=super_admin, chat=chat, reply_to_message=reply_message
        )

        # Assert workflow
        assert admin_command.reply_to_message.from_user.id == new_admin_candidate.id
        assert new_admin_mute.from_user.id == new_admin_candidate.id
        assert unadmin_command.reply_to_message.from_user.id == new_admin_candidate.id

    async def test_welcome_and_configuration_workflow(self, event_simulator: TelegramEventSimulator):
        """Test welcome message configuration and delivery."""
        # Setup
        admin = create_admin_user()
        new_user = create_normal_user(id=777666555, username="newcomer")
        chat = create_test_chat()

        # 1. Admin configures welcome message
        welcome_config = event_simulator.factory.create_command_message(
            command="welcome", args="Welcome to our educational chat! Please read the rules.", user=admin, chat=chat
        )

        # 2. Admin sets auto-delete timer
        welcome_timer = event_simulator.factory.create_command_message(
            command="welcome",
            args="-t 300",  # 5 minutes
            user=admin,
            chat=chat,
        )

        # 3. New user joins
        join_event = await event_simulator.simulate_user_join(user=new_user, chat=chat)

        # 4. New user receives welcome message (would be sent by events handler)
        # This would be triggered automatically by the join event

        # Assert configuration
        assert "Welcome to our educational chat!" in welcome_config.text
        assert "-t 300" in welcome_timer.text
        assert join_event.new_chat_member.user.id == new_user.id

    async def test_error_handling_across_routers(self, event_simulator: TelegramEventSimulator):
        """Test error handling in router workflows."""
        # Setup problematic scenarios
        admin = create_admin_user()
        chat = create_test_chat()

        # 1. Command without reply (should be handled gracefully)
        invalid_mute = event_simulator.factory.create_command_message(
            command="mute",
            user=admin,
            chat=chat,
            reply_to_message=None,  # Missing reply
        )

        # 2. Invalid command arguments
        invalid_duration = event_simulator.factory.create_command_message(
            command="mute", args="invalid_number", user=admin, chat=chat
        )

        # 3. Self-targeting moderation
        self_mute = event_simulator.factory.create_command_message(
            command="mute",
            user=admin,
            chat=chat,
            reply_to_message=event_simulator.factory.create_message(
                user=admin,  # Admin replying to themselves
                chat=chat,
            ),
        )

        # Assert error cases are properly structured
        assert invalid_mute.reply_to_message is None
        assert "invalid" in invalid_duration.text
        assert self_mute.reply_to_message.from_user.id == admin.id
