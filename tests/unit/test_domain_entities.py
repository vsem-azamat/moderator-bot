"""Unit tests for domain entities."""

import pytest
from app.domain.entities import ChatEntity, MessageEntity, UserEntity

from tests.factories import AdminFactory, ChatFactory, ChatLinkFactory, MessageFactory, UserFactory


class TestUserEntity:
    """Test cases for UserEntity."""

    def test_create_user_entity(self):
        """Test creating a user entity with all fields."""
        user = UserFactory.create(
            id=123456789, username="testuser", first_name="Test", last_name="User", is_verified=True, is_blocked=False
        )

        assert user.id == 123456789
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_verified is True
        assert user.is_blocked is False

    def test_user_display_name_full_name(self):
        """Test display name with first and last name."""
        user = UserFactory.create(first_name="John", last_name="Doe", username="johndoe")

        assert user.display_name == "John Doe"

    def test_user_display_name_first_name_only(self):
        """Test display name with only first name."""
        user = UserEntity(id=123456, first_name="John", last_name=None, username="johndoe")

        assert user.display_name == "John"

    def test_user_display_name_username_only(self):
        """Test display name with only username."""
        user = UserEntity(id=123456, first_name=None, last_name=None, username="johndoe")

        assert user.display_name == "@johndoe"

    def test_user_display_name_fallback(self):
        """Test display name fallback to user ID."""
        user = UserEntity(id=123456, first_name=None, last_name=None, username=None)

        assert user.display_name == "User 123456"

    def test_block_user(self):
        """Test blocking a user."""
        user = UserFactory.create(is_blocked=False)

        user.block()

        assert user.is_blocked is True

    def test_unblock_user(self):
        """Test unblocking a user."""
        user = UserFactory.create_blocked()

        user.unblock()

        assert user.is_blocked is False

    def test_user_equality(self):
        """Test user entity equality."""
        user1 = UserFactory.create(id=123456)
        user2 = UserFactory.create(id=123456)
        user3 = UserFactory.create(id=654321)

        # Same ID should be equal (for business logic)
        assert user1.id == user2.id
        assert user1.id != user3.id


class TestChatEntity:
    """Test cases for ChatEntity."""

    def test_create_chat_entity(self):
        """Test creating a chat entity."""
        chat = ChatFactory.create(
            id=-1001234567890,
            title="Test Chat",
            is_forum=False,
            welcome_message="Welcome!",
            welcome_delete_time=60,
            is_welcome_enabled=True,
            is_captcha_enabled=False,
        )

        assert chat.id == -1001234567890
        assert chat.title == "Test Chat"
        assert chat.is_forum is False
        assert chat.welcome_message == "Welcome!"
        assert chat.welcome_delete_time == 60
        assert chat.is_welcome_enabled is True
        assert chat.is_captcha_enabled is False

    def test_enable_welcome_message(self):
        """Test enabling welcome message."""
        chat = ChatFactory.create(is_welcome_enabled=False)

        chat.enable_welcome("Hello everyone!")

        assert chat.is_welcome_enabled is True
        assert chat.welcome_message == "Hello everyone!"

    def test_enable_welcome_without_message(self):
        """Test enabling welcome without changing message."""
        chat = ChatFactory.create(welcome_message="Original message", is_welcome_enabled=False)

        chat.enable_welcome()

        assert chat.is_welcome_enabled is True
        assert chat.welcome_message == "Original message"

    def test_disable_welcome_message(self):
        """Test disabling welcome message."""
        chat = ChatFactory.create_with_welcome()

        chat.disable_welcome()

        assert chat.is_welcome_enabled is False

    def test_set_welcome_delete_time_valid(self):
        """Test setting valid welcome delete time."""
        chat = ChatFactory.create()

        chat.set_welcome_delete_time(120)

        assert chat.welcome_delete_time == 120

    def test_set_welcome_delete_time_invalid(self):
        """Test setting invalid welcome delete time."""
        chat = ChatFactory.create()

        with pytest.raises(ValueError, match="Delete time must be positive"):
            chat.set_welcome_delete_time(0)

        with pytest.raises(ValueError, match="Delete time must be positive"):
            chat.set_welcome_delete_time(-10)

    def test_enable_captcha(self):
        """Test enabling captcha."""
        chat = ChatFactory.create(is_captcha_enabled=False)

        chat.enable_captcha()

        assert chat.is_captcha_enabled is True

    def test_disable_captcha(self):
        """Test disabling captcha."""
        chat = ChatFactory.create(is_captcha_enabled=True)

        chat.disable_captcha()

        assert chat.is_captcha_enabled is False


class TestAdminEntity:
    """Test cases for AdminEntity."""

    def test_create_admin_entity(self):
        """Test creating an admin entity."""
        admin = AdminFactory.create(id=123456789, is_active=True)

        assert admin.id == 123456789
        assert admin.is_active is True

    def test_activate_admin(self):
        """Test activating an admin."""
        admin = AdminFactory.create_inactive()

        admin.activate()

        assert admin.is_active is True

    def test_deactivate_admin(self):
        """Test deactivating an admin."""
        admin = AdminFactory.create(is_active=True)

        admin.deactivate()

        assert admin.is_active is False


class TestMessageEntity:
    """Test cases for MessageEntity."""

    def test_create_message_entity(self):
        """Test creating a message entity."""
        message = MessageFactory.create(
            id=1,
            chat_id=-1001234567890,
            user_id=123456789,
            message_id=42,
            content="Hello, world!",
            metadata={"type": "text"},
            is_spam=False,
        )

        assert message.id == 1
        assert message.chat_id == -1001234567890
        assert message.user_id == 123456789
        assert message.message_id == 42
        assert message.content == "Hello, world!"
        assert message.metadata == {"type": "text"}
        assert message.is_spam is False

    def test_mark_message_as_spam(self):
        """Test marking message as spam."""
        message = MessageFactory.create(is_spam=False)

        message.mark_as_spam()

        assert message.is_spam is True

    def test_unmark_message_as_spam(self):
        """Test unmarking message as spam."""
        message = MessageFactory.create_spam()

        message.unmark_as_spam()

        assert message.is_spam is False

    def test_message_with_empty_metadata(self):
        """Test message with empty metadata."""
        message = MessageFactory.create(metadata=None)

        # Should handle None metadata gracefully
        assert message.metadata is None or message.metadata == {}


class TestChatLinkEntity:
    """Test cases for ChatLinkEntity."""

    def test_create_chat_link_entity(self):
        """Test creating a chat link entity."""
        link = ChatLinkFactory.create(id=1, text="Educational Chat", link="https://t.me/educhat", priority=5)

        assert link.id == 1
        assert link.text == "Educational Chat"
        assert link.link == "https://t.me/educhat"
        assert link.priority == 5

    def test_update_priority(self):
        """Test updating link priority."""
        link = ChatLinkFactory.create(priority=0)

        link.update_priority(10)

        assert link.priority == 10

    def test_update_priority_negative(self):
        """Test updating with negative priority."""
        link = ChatLinkFactory.create(priority=5)

        link.update_priority(-1)

        assert link.priority == -1


@pytest.mark.unit
class TestEntityValidation:
    """Test entity validation and edge cases."""

    def test_user_with_minimal_data(self):
        """Test creating user with minimal required data."""
        user = UserEntity(id=123)

        assert user.id == 123
        assert user.username is None
        assert user.first_name is None
        assert user.last_name is None
        assert user.is_verified is True  # Default value
        assert user.is_blocked is False  # Default value

    def test_chat_with_minimal_data(self):
        """Test creating chat with minimal required data."""
        chat = ChatEntity(id=-123)

        assert chat.id == -123
        assert chat.title is None
        assert chat.is_forum is False  # Default value
        assert chat.welcome_delete_time == 60  # Default value

    def test_message_with_minimal_data(self):
        """Test creating message with minimal required data."""
        message = MessageEntity(id=None, chat_id=-123, user_id=456, message_id=789)

        assert message.id is None
        assert message.chat_id == -123
        assert message.user_id == 456
        assert message.message_id == 789
        assert message.content is None
        assert message.is_spam is False  # Default value
