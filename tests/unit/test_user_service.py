"""Unit tests for UserService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.application.services.user_service import UserService
from app.domain.entities import UserEntity
from app.domain.exceptions import UserNotFoundException
from app.domain.repositories import IUserRepository

from tests.factories import UserFactory

# Constants for patch paths
BOT_LOGGER_PATCH_PATH = "app.application.services.user_service.BotLogger"


class TestUserService:
    """Test cases for UserService."""

    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        """Create a mock user repository."""
        return AsyncMock(spec=IUserRepository)

    @pytest.fixture
    def user_service(self, mock_user_repository: AsyncMock) -> UserService:
        """Create UserService with mocked dependencies."""
        return UserService(mock_user_repository)

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test successfully getting user by ID."""
        # Arrange
        user_id = 123456789
        expected_user = UserFactory.create(id=user_id)
        mock_user_repository.get_by_id.return_value = expected_user

        # Act
        result = await user_service.get_user_by_id(user_id)

        # Assert
        assert result == expected_user
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test getting user by ID when user doesn't exist."""
        # Arrange
        user_id = 999999999
        mock_user_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundException) as exc_info:
            await user_service.get_user_by_id(user_id)

        assert exc_info.value.user_id == user_id
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_id_optional_success(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test successfully getting user by ID (optional)."""
        # Arrange
        user_id = 123456789
        expected_user = UserFactory.create(id=user_id)
        mock_user_repository.get_by_id.return_value = expected_user

        # Act
        result = await user_service.get_user_by_id_optional(user_id)

        # Assert
        assert result == expected_user
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_id_optional_not_found(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test getting user by ID (optional) when user doesn't exist."""
        # Arrange
        user_id = 999999999
        mock_user_repository.get_by_id.return_value = None

        # Act
        result = await user_service.get_user_by_id_optional(user_id)

        # Assert
        assert result is None
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_create_or_update_user_new_user(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test creating a new user."""
        # Arrange
        user_id = 123456789
        username = "testuser"
        first_name = "Test"
        last_name = "User"

        mock_user_repository.get_by_id.return_value = None
        mock_user_repository.save.return_value = UserFactory.create(
            id=user_id, username=username, first_name=first_name, last_name=last_name
        )

        # Act
        with patch(BOT_LOGGER_PATCH_PATH) as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            user_service = UserService(mock_user_repository)
            result = await user_service.create_or_update_user(
                user_id=user_id, username=username, first_name=first_name, last_name=last_name
            )

        # Assert
        assert result.id == user_id
        assert result.username == username
        assert result.first_name == first_name
        assert result.last_name == last_name

        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.save.assert_called_once()
        mock_logger.log_user_action.assert_called_once_with(user_id, "user_created")

    @pytest.mark.asyncio
    async def test_create_or_update_user_existing_user(
        self, user_service: UserService, mock_user_repository: AsyncMock
    ):
        """Test updating an existing user."""
        # Arrange
        user_id = 123456789
        existing_user = UserFactory.create(id=user_id, username="oldusername", first_name="Old", last_name="Name")

        updated_user = UserFactory.create(id=user_id, username="newusername", first_name="New", last_name="Name")

        mock_user_repository.get_by_id.return_value = existing_user
        mock_user_repository.save.return_value = updated_user

        # Act
        with patch(BOT_LOGGER_PATCH_PATH) as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            user_service = UserService(mock_user_repository)
            result = await user_service.create_or_update_user(
                user_id=user_id, username="newusername", first_name="New", last_name="Name"
            )

        # Assert
        assert result.username == "newusername"
        assert result.first_name == "New"

        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.save.assert_called_once()
        mock_logger.log_user_action.assert_called_once_with(user_id, "profile_updated")

    @pytest.mark.asyncio
    async def test_block_user_existing_user(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test blocking an existing user."""
        # Arrange
        user_id = 123456789
        existing_user = UserFactory.create(id=user_id, is_blocked=False)
        blocked_user = UserFactory.create(id=user_id, is_blocked=True)

        mock_user_repository.get_by_id.return_value = existing_user
        mock_user_repository.save.return_value = blocked_user

        # Act
        with patch(BOT_LOGGER_PATCH_PATH) as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            user_service = UserService(mock_user_repository)
            result = await user_service.block_user(user_id)

        # Assert
        assert result.is_blocked is True

        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.save.assert_called_once()
        mock_logger.log_user_action.assert_called_once_with(user_id, "user_blocked")

    @pytest.mark.asyncio
    async def test_block_user_nonexistent_user(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test blocking a non-existent user (creates new blocked user)."""
        # Arrange
        user_id = 123456789
        new_blocked_user = UserFactory.create(id=user_id, is_blocked=True)

        mock_user_repository.get_by_id.return_value = None
        mock_user_repository.save.return_value = new_blocked_user

        # Act
        with patch(BOT_LOGGER_PATCH_PATH) as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            user_service = UserService(mock_user_repository)
            result = await user_service.block_user(user_id)

        # Assert
        assert result.is_blocked is True
        assert result.id == user_id

        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.save.assert_called_once()
        mock_logger.log_user_action.assert_called_once_with(user_id, "user_blocked")

    @pytest.mark.asyncio
    async def test_unblock_user_success(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test successfully unblocking a user."""
        # Arrange
        user_id = 123456789
        blocked_user = UserFactory.create(id=user_id, is_blocked=True)
        unblocked_user = UserFactory.create(id=user_id, is_blocked=False)

        mock_user_repository.get_by_id.return_value = blocked_user
        mock_user_repository.save.return_value = unblocked_user

        # Act
        with patch(BOT_LOGGER_PATCH_PATH) as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            user_service = UserService(mock_user_repository)
            result = await user_service.unblock_user(user_id)

        # Assert
        assert result.is_blocked is False

        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.save.assert_called_once()
        mock_logger.log_user_action.assert_called_once_with(user_id, "user_unblocked")

    @pytest.mark.asyncio
    async def test_unblock_user_not_blocked(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test unblocking a user that isn't blocked."""
        # Arrange
        user_id = 123456789
        user = UserFactory.create(id=user_id, is_blocked=False)

        mock_user_repository.get_by_id.return_value = user

        # Act
        with patch(BOT_LOGGER_PATCH_PATH) as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            user_service = UserService(mock_user_repository)
            result = await user_service.unblock_user(user_id)

        # Assert
        assert result.is_blocked is False

        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        # save should not be called since user wasn't blocked
        mock_user_repository.save.assert_not_called()
        mock_logger.log_user_action.assert_called_once_with(user_id, "unblock_attempt_not_blocked")

    @pytest.mark.asyncio
    async def test_unblock_user_not_found(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test unblocking a user that doesn't exist."""
        # Arrange
        user_id = 999999999
        mock_user_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundException) as exc_info:
            await user_service.unblock_user(user_id)

        assert exc_info.value.user_id == user_id
        mock_user_repository.get_by_id.assert_called_once_with(user_id)
        mock_user_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_blocked_users(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test getting all blocked users."""
        # Arrange
        blocked_users = UserFactory.create_batch(3, is_blocked=True)
        mock_user_repository.get_blocked_users.return_value = blocked_users

        # Act
        result = await user_service.get_blocked_users()

        # Assert
        assert result == blocked_users
        assert len(result) == 3
        assert all(user.is_blocked for user in result)
        mock_user_repository.get_blocked_users.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_blocked_users_empty(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test getting blocked users when none exist."""
        # Arrange
        mock_user_repository.get_blocked_users.return_value = []

        # Act
        result = await user_service.get_blocked_users()

        # Assert
        assert result == []
        mock_user_repository.get_blocked_users.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_user_blocked_true(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test checking if user is blocked (user exists and is blocked)."""
        # Arrange
        user_id = 123456789
        blocked_user = UserFactory.create(id=user_id, is_blocked=True)
        mock_user_repository.get_by_id.return_value = blocked_user

        # Act
        result = await user_service.is_user_blocked(user_id)

        # Assert
        assert result is True
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_is_user_blocked_false(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test checking if user is blocked (user exists but not blocked)."""
        # Arrange
        user_id = 123456789
        user = UserFactory.create(id=user_id, is_blocked=False)
        mock_user_repository.get_by_id.return_value = user

        # Act
        result = await user_service.is_user_blocked(user_id)

        # Assert
        assert result is False
        mock_user_repository.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_is_user_blocked_user_not_exists(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test checking if user is blocked (user doesn't exist)."""
        # Arrange
        user_id = 999999999
        mock_user_repository.get_by_id.return_value = None

        # Act
        result = await user_service.is_user_blocked(user_id)

        # Assert
        assert result is False
        mock_user_repository.get_by_id.assert_called_once_with(user_id)


@pytest.mark.unit
class TestUserServiceEdgeCases:
    """Test edge cases and error conditions for UserService."""

    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        """Create a mock user repository."""
        return AsyncMock(spec=IUserRepository)

    @pytest.fixture
    def user_service(self, mock_user_repository: AsyncMock) -> UserService:
        """Create UserService with mocked dependencies."""
        return UserService(mock_user_repository)

    @pytest.mark.asyncio
    async def test_create_or_update_user_partial_data(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test creating user with partial data (some None values)."""
        # Arrange
        user_id = 123456789
        mock_user_repository.get_by_id.return_value = None
        expected_user = UserEntity(
            id=user_id, username=None, first_name="Test", last_name=None, is_verified=False, is_blocked=False
        )
        mock_user_repository.save.return_value = expected_user

        # Act
        with patch(BOT_LOGGER_PATCH_PATH):
            result = await user_service.create_or_update_user(
                user_id=user_id, username=None, first_name="Test", last_name=None
            )

        # Assert
        assert result.id == user_id
        assert result.username is None
        assert result.first_name == "Test"
        assert result.last_name is None

    @pytest.mark.asyncio
    async def test_repository_exception_handling(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test handling repository exceptions."""
        # Arrange
        user_id = 123456789
        mock_user_repository.get_by_id.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await user_service.get_user_by_id(user_id)

    @pytest.mark.asyncio
    async def test_multiple_operations_same_user(self, user_service: UserService, mock_user_repository: AsyncMock):
        """Test multiple operations on the same user."""
        # Arrange
        user_id = 123456789
        user = UserFactory.create(id=user_id, is_blocked=False)
        blocked_user = UserFactory.create(id=user_id, is_blocked=True)
        unblocked_user = UserFactory.create(id=user_id, is_blocked=False)

        # Setup mock to return different states
        mock_user_repository.get_by_id.side_effect = [user, blocked_user]
        mock_user_repository.save.side_effect = [blocked_user, unblocked_user]

        # Act
        with patch(BOT_LOGGER_PATCH_PATH):
            # Block user
            result1 = await user_service.block_user(user_id)
            assert result1.is_blocked is True

            # Unblock user
            result2 = await user_service.unblock_user(user_id)
            assert result2.is_blocked is False

        # Assert
        assert mock_user_repository.get_by_id.call_count == 2
        assert mock_user_repository.save.call_count == 2
