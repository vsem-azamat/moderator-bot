"""Dependency injection container."""

from typing import Any, TypeVar

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.repositories import (
    IAdminRepository,
    IChatLinkRepository,
    IChatRepository,
    IMessageRepository,
    IUserRepository,
)
from app.infrastructure.db.repositories.admin import AdminRepository
from app.infrastructure.db.repositories.chat import ChatRepository
from app.infrastructure.db.repositories.chat_link import ChatLinkRepository
from app.infrastructure.db.repositories.message import MessageRepository
from app.infrastructure.db.repositories.user import UserRepository

T = TypeVar("T")


class Container:
    """Dependency injection container."""

    def __init__(self) -> None:
        self._services: dict[type[Any], Any] = {}
        self._singletons: dict[type[Any], Any] = {}
        self._session_maker: async_sessionmaker[AsyncSession] | None = None
        self._bot: Bot | None = None

    def register_singleton(self, interface: type[T], implementation: T) -> None:
        """Register a singleton service."""
        self._singletons[interface] = implementation

    def register_transient(self, interface: type[T], implementation_factory: Any) -> None:
        """Register a transient service with factory."""
        self._services[interface] = implementation_factory

    def set_session_maker(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        """Set database session maker."""
        self._session_maker = session_maker

    def set_bot(self, bot: Bot) -> None:
        """Set bot instance."""
        self._bot = bot

    def get(self, interface: type[T]) -> T:
        """Get service instance."""
        # Check singletons first
        if interface in self._singletons:
            return self._singletons[interface]  # type: ignore

        # Check transient services
        if interface in self._services:
            factory = self._services[interface]
            return factory()  # type: ignore

        raise ValueError(f"Service {interface} not registered")

    def get_session(self) -> AsyncSession:
        """Get database session."""
        if not self._session_maker:
            raise ValueError("Session maker not set")
        return self._session_maker()

    def get_bot(self) -> Bot:
        """Get bot instance."""
        if not self._bot:
            raise ValueError("Bot not set")
        return self._bot

    def get_user_repository(self, session: AsyncSession) -> IUserRepository:
        """Get user repository."""
        return UserRepository(session)

    def get_chat_repository(self, session: AsyncSession) -> IChatRepository:
        """Get chat repository."""
        return ChatRepository(session)

    def get_admin_repository(self, session: AsyncSession) -> IAdminRepository:
        """Get admin repository."""
        return AdminRepository(session)

    def get_message_repository(self, session: AsyncSession) -> IMessageRepository:
        """Get message repository."""
        return MessageRepository(session)

    def get_chat_link_repository(self, session: AsyncSession) -> IChatLinkRepository:
        """Get chat link repository."""
        return ChatLinkRepository(session)


# Global container instance
container = Container()


def setup_container(session_maker: async_sessionmaker[AsyncSession], bot: Bot) -> None:
    """Setup dependency injection container."""
    container.set_session_maker(session_maker)
    container.set_bot(bot)

    # Register repository factories
    container.register_transient(IUserRepository, lambda: container.get_user_repository(container.get_session()))
    container.register_transient(IChatRepository, lambda: container.get_chat_repository(container.get_session()))
    container.register_transient(IAdminRepository, lambda: container.get_admin_repository(container.get_session()))
    container.register_transient(IMessageRepository, lambda: container.get_message_repository(container.get_session()))
    container.register_transient(
        IChatLinkRepository, lambda: container.get_chat_link_repository(container.get_session())
    )
