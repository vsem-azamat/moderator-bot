"""Test data factories for creating test objects."""

import random
from datetime import datetime

from app.domain.entities import AdminEntity, ChatEntity, ChatLinkEntity, MessageEntity, UserEntity
from app.domain.value_objects import MuteDuration, UserProfile, WelcomeSettings


class UserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create(
        id: int | None = None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        is_verified: bool = True,
        is_blocked: bool = False,
        created_at: datetime | None = None,
        modified_at: datetime | None = None,
    ) -> UserEntity:
        """Create a test user entity."""
        return UserEntity(
            id=id or random.randint(100000000, 999999999),
            username=username or f"testuser{random.randint(1000, 9999)}",
            first_name=first_name or f"Test{random.randint(1, 100)}",
            last_name=last_name or f"User{random.randint(1, 100)}",
            is_verified=is_verified,
            is_blocked=is_blocked,
            created_at=created_at or datetime.now(),
            modified_at=modified_at or datetime.now(),
        )

    @staticmethod
    def create_blocked(id: int | None = None, **kwargs) -> UserEntity:
        """Create a blocked test user."""
        return UserFactory.create(id=id, is_blocked=True, **kwargs)

    @staticmethod
    def create_unverified(id: int | None = None, **kwargs) -> UserEntity:
        """Create an unverified test user."""
        return UserFactory.create(id=id, is_verified=False, **kwargs)

    @staticmethod
    def create_batch(count: int, **kwargs) -> list[UserEntity]:
        """Create multiple test users."""
        return [UserFactory.create(**kwargs) for _ in range(count)]


class ChatFactory:
    """Factory for creating test chats."""

    @staticmethod
    def create(
        id: int | None = None,
        title: str | None = None,
        is_forum: bool = False,
        welcome_message: str | None = None,
        welcome_delete_time: int = 60,
        is_welcome_enabled: bool = False,
        is_captcha_enabled: bool = False,
        created_at: datetime | None = None,
        modified_at: datetime | None = None,
    ) -> ChatEntity:
        """Create a test chat entity."""
        return ChatEntity(
            id=id or -random.randint(1000000000000, 9999999999999),
            title=title or f"Test Chat {random.randint(1, 1000)}",
            is_forum=is_forum,
            welcome_message=welcome_message,
            welcome_delete_time=welcome_delete_time,
            is_welcome_enabled=is_welcome_enabled,
            is_captcha_enabled=is_captcha_enabled,
            created_at=created_at or datetime.now(),
            modified_at=modified_at or datetime.now(),
        )

    @staticmethod
    def create_with_welcome(message: str = "Welcome to our chat!", delete_time: int = 60, **kwargs) -> ChatEntity:
        """Create a chat with welcome message enabled."""
        return ChatFactory.create(
            welcome_message=message, welcome_delete_time=delete_time, is_welcome_enabled=True, **kwargs
        )

    @staticmethod
    def create_forum(**kwargs) -> ChatEntity:
        """Create a forum chat."""
        return ChatFactory.create(is_forum=True, **kwargs)

    @staticmethod
    def create_batch(count: int, **kwargs) -> list[ChatEntity]:
        """Create multiple test chats."""
        return [ChatFactory.create(**kwargs) for _ in range(count)]


class AdminFactory:
    """Factory for creating test admins."""

    @staticmethod
    def create(
        id: int | None = None,
        is_active: bool = True,
    ) -> AdminEntity:
        """Create a test admin entity."""
        return AdminEntity(
            id=id or random.randint(100000000, 999999999),
            is_active=is_active,
        )

    @staticmethod
    def create_inactive(**kwargs) -> AdminEntity:
        """Create an inactive admin."""
        return AdminFactory.create(is_active=False, **kwargs)

    @staticmethod
    def create_batch(count: int, **kwargs) -> list[AdminEntity]:
        """Create multiple test admins."""
        return [AdminFactory.create(**kwargs) for _ in range(count)]


class MessageFactory:
    """Factory for creating test messages."""

    @staticmethod
    def create(
        id: int | None = None,
        chat_id: int | None = None,
        user_id: int | None = None,
        message_id: int | None = None,
        content: str | None = None,
        metadata: dict | None = None,
        timestamp: datetime | None = None,
        is_spam: bool = False,
    ) -> MessageEntity:
        """Create a test message entity."""
        return MessageEntity(
            id=id,
            chat_id=chat_id or -random.randint(1000000000000, 9999999999999),
            user_id=user_id or random.randint(100000000, 999999999),
            message_id=message_id or random.randint(1, 100000),
            content=content or f"Test message {random.randint(1, 1000)}",
            metadata=metadata or {},
            timestamp=timestamp or datetime.now(),
            is_spam=is_spam,
        )

    @staticmethod
    def create_spam(**kwargs) -> MessageEntity:
        """Create a spam message."""
        return MessageFactory.create(is_spam=True, **kwargs)

    @staticmethod
    def create_batch(count: int, **kwargs) -> list[MessageEntity]:
        """Create multiple test messages."""
        return [MessageFactory.create(**kwargs) for _ in range(count)]


class ChatLinkFactory:
    """Factory for creating test chat links."""

    @staticmethod
    def create(
        id: int | None = None,
        text: str | None = None,
        link: str | None = None,
        priority: int = 0,
    ) -> ChatLinkEntity:
        """Create a test chat link entity."""
        random_id = random.randint(1, 1000)
        return ChatLinkEntity(
            id=id,
            text=text or f"Test Chat Link {random_id}",
            link=link or f"https://t.me/testchat{random_id}",
            priority=priority,
        )

    @staticmethod
    def create_high_priority(**kwargs) -> ChatLinkEntity:
        """Create a high priority chat link."""
        return ChatLinkFactory.create(priority=10, **kwargs)

    @staticmethod
    def create_batch(count: int, **kwargs) -> list[ChatLinkEntity]:
        """Create multiple test chat links."""
        return [ChatLinkFactory.create(**kwargs) for _ in range(count)]


class ValueObjectFactory:
    """Factory for creating test value objects."""

    @staticmethod
    def create_mute_duration(minutes: int = 5) -> MuteDuration:
        """Create a test mute duration."""
        return MuteDuration(minutes=minutes)

    @staticmethod
    def create_user_profile(
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> UserProfile:
        """Create a test user profile."""
        return UserProfile(
            username=username or f"testuser{random.randint(1000, 9999)}",
            first_name=first_name or f"Test{random.randint(1, 100)}",
            last_name=last_name or f"User{random.randint(1, 100)}",
        )

    @staticmethod
    def create_welcome_settings(
        enabled: bool = True,
        message: str | None = None,
        delete_after_seconds: int = 60,
        captcha_enabled: bool = False,
    ) -> WelcomeSettings:
        """Create test welcome settings."""
        return WelcomeSettings(
            enabled=enabled,
            message=message or "Welcome to our test chat!",
            delete_after_seconds=delete_after_seconds,
            captcha_enabled=captcha_enabled,
        )


class TestDataBuilder:
    """Builder pattern for creating complex test scenarios."""

    @staticmethod
    def create_chat_with_users_and_messages(
        user_count: int = 3,
        message_count_per_user: int = 2,
    ) -> tuple[ChatEntity, list[UserEntity], list[MessageEntity]]:
        """Create a chat with users and their messages."""
        chat = ChatFactory.create()
        users = UserFactory.create_batch(user_count)
        messages = []

        for user in users:
            for _ in range(message_count_per_user):
                message = MessageFactory.create(
                    chat_id=chat.id,
                    user_id=user.id,
                )
                messages.append(message)

        return chat, users, messages

    @staticmethod
    def create_moderation_scenario(
        admin_count: int = 2,
        user_count: int = 5,
        chat_count: int = 3,
    ) -> tuple[list[AdminEntity], list[UserEntity], list[ChatEntity]]:
        """Create a complete moderation scenario."""
        admins = AdminFactory.create_batch(admin_count)
        users = UserFactory.create_batch(user_count)
        chats = ChatFactory.create_batch(chat_count)

        # Block some users
        if len(users) >= 2:
            users[0].block()
            users[1].block()

        return admins, users, chats
