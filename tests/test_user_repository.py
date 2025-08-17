import pytest
from app.domain.entities import UserEntity
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

    async def test_find_blocked_user(self, session):
        """Test finding blocked users by username or ID."""
        repo = UserRepository(session)

        # Create test users
        user1 = UserEntity(id=123, username="testuser", first_name="Test", is_blocked=True)
        user2 = UserEntity(id=456, username="spammer", first_name="Spam", is_blocked=True)
        user3 = UserEntity(id=789, username=None, first_name="NoUsername", is_blocked=False)  # Not blocked

        await repo.save(user1)
        await repo.save(user2)
        await repo.save(user3)

        # Test find by username with @
        found_user = await repo.find_blocked_user("@testuser")
        assert found_user is not None
        assert found_user.id == 123
        assert found_user.username == "testuser"

        # Test find by username without @
        found_user = await repo.find_blocked_user("spammer")
        assert found_user is not None
        assert found_user.id == 456

        # Test find by user ID
        found_user = await repo.find_blocked_user("123")
        assert found_user is not None
        assert found_user.id == 123

        # Test find non-blocked user (should return None)
        found_user = await repo.find_blocked_user("789")
        assert found_user is None

        # Test find non-existent user
        found_user = await repo.find_blocked_user("@nonexistent")
        assert found_user is None

        # Test find non-existent ID
        found_user = await repo.find_blocked_user("999")
        assert found_user is None
