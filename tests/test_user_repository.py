import pytest
from app.infrastructure.db.repositories.user import UserRepository

from tests.factories import UserFactory


@pytest.mark.integration
class TestUserRepository:
    """Integration tests for UserRepository."""

    @pytest.mark.asyncio
    async def test_save_and_get_user(self, session):
        """Test saving and retrieving a user."""
        # Arrange
        repo = UserRepository(session)
        user = UserFactory.create(id=123456789, username="testuser")

        # Act
        saved_user = await repo.save(user)
        retrieved_user = await repo.get_by_id(user.id)

        # Assert
        assert saved_user.id == user.id
        assert saved_user.username == user.username
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.username == user.username

    @pytest.mark.asyncio
    async def test_get_blocked_users(self, session):
        """Test getting blocked users."""
        # Arrange
        repo = UserRepository(session)
        blocked_user = UserFactory.create_blocked(id=123456789)
        normal_user = UserFactory.create(id=987654321)

        # Act
        await repo.save(blocked_user)
        await repo.save(normal_user)
        blocked_users = await repo.get_blocked_users()

        # Assert
        assert len(blocked_users) == 1
        assert blocked_users[0].id == blocked_user.id
        assert blocked_users[0].is_blocked is True

    @pytest.mark.asyncio
    async def test_user_exists(self, session):
        """Test checking if user exists."""
        # Arrange
        repo = UserRepository(session)
        user = UserFactory.create(id=123456789)

        # Act
        await repo.save(user)
        exists = await repo.exists(user.id)
        not_exists = await repo.exists(999999999)

        # Assert
        assert exists is True
        assert not_exists is False

    @pytest.mark.asyncio
    async def test_legacy_blacklist_methods(self, session):
        """Test legacy blacklist methods for backward compatibility."""
        # Arrange
        repo = UserRepository(session)
        user_id = 123456789

        # Act - Add to blacklist
        await repo.add_to_blacklist(user_id)
        blocked_users = await repo.get_blocked_users()

        # Assert - User should be blocked
        assert len(blocked_users) == 1
        assert blocked_users[0].id == user_id
        assert blocked_users[0].is_blocked is True

        # Act - Remove from blacklist
        await repo.remove_from_blacklist(user_id)
        blocked_users_after = await repo.get_blocked_users()

        # Assert - No blocked users
        assert len(blocked_users_after) == 0
