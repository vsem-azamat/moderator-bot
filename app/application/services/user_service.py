"""User domain service."""

from app.core.logging import BotLogger
from app.domain.entities import UserEntity
from app.domain.exceptions import UserNotFoundException
from app.domain.repositories import IUserRepository


class UserService:
    """User domain service."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self.user_repository = user_repository
        self.logger = BotLogger("user_service")

    async def get_user_by_id(self, user_id: int) -> UserEntity:
        """Get user by ID, raise exception if not found."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user

    async def get_user_by_id_optional(self, user_id: int) -> UserEntity | None:
        """Get user by ID, return None if not found."""
        return await self.user_repository.get_by_id(user_id)

    async def create_or_update_user(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> UserEntity:
        """Create or update user with profile information."""
        existing_user = await self.user_repository.get_by_id(user_id)

        if existing_user:
            # Update existing user
            existing_user.username = username
            existing_user.first_name = first_name
            existing_user.last_name = last_name
            user = await self.user_repository.save(existing_user)
            self.logger.log_user_action(user_id, "profile_updated")
        else:
            # Create new user
            user = UserEntity(
                id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            user = await self.user_repository.save(user)
            self.logger.log_user_action(user_id, "user_created")

        return user

    async def block_user(self, user_id: int) -> UserEntity:
        """Block user (add to blacklist)."""
        user = await self.get_user_by_id_optional(user_id)

        if not user:
            # Create user record if doesn't exist
            user = UserEntity(id=user_id, is_blocked=True)
        else:
            user.block()

        user = await self.user_repository.save(user)
        self.logger.log_user_action(user_id, "user_blocked")
        return user

    async def unblock_user(self, user_id: int) -> UserEntity:
        """Unblock user (remove from blacklist)."""
        user = await self.get_user_by_id(user_id)

        if not user.is_blocked:
            self.logger.log_user_action(user_id, "unblock_attempt_not_blocked")
            return user

        user.unblock()
        user = await self.user_repository.save(user)
        self.logger.log_user_action(user_id, "user_unblocked")
        return user

    async def get_blocked_users(self) -> list[UserEntity]:
        """Get all blocked users."""
        return await self.user_repository.get_blocked_users()

    async def is_user_blocked(self, user_id: int) -> bool:
        """Check if user is blocked."""
        user = await self.user_repository.get_by_id(user_id)
        return user.is_blocked if user else False
