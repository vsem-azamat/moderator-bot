"""Integration tests for UserRepository."""

import pytest
from app.domain.entities import UserEntity
from app.domain.repositories import IUserRepository

from tests.factories import UserFactory


@pytest.mark.integration
class TestUserRepositoryIntegration:
    """Integration tests for UserRepository."""

    async def test_save_and_get_user(self, user_repository: IUserRepository, sample_user_data: dict):
        """Test saving and retrieving a user."""
        # Create user entity
        user = UserFactory.create(**sample_user_data)

        # Save user
        saved_user = await user_repository.save(user)

        # Verify save
        assert saved_user.id == user.id
        assert saved_user.username == user.username
        assert saved_user.first_name == user.first_name

        # Retrieve user
        retrieved_user = await user_repository.get_by_id(user.id)

        # Verify retrieval
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.username == user.username
        assert retrieved_user.first_name == user.first_name
        assert retrieved_user.last_name == user.last_name

    async def test_get_nonexistent_user(self, user_repository: IUserRepository):
        """Test getting a user that doesn't exist."""
        nonexistent_id = 999999999

        user = await user_repository.get_by_id(nonexistent_id)

        assert user is None

    async def test_user_exists(self, user_repository: IUserRepository):
        """Test checking if user exists."""
        user = UserFactory.create()

        # User doesn't exist yet
        exists_before = await user_repository.exists(user.id)
        assert exists_before is False

        # Save user
        await user_repository.save(user)

        # User exists now
        exists_after = await user_repository.exists(user.id)
        assert exists_after is True

    async def test_update_existing_user(self, user_repository: IUserRepository):
        """Test updating an existing user."""
        # Create and save user
        user = UserFactory.create(username="original_username", first_name="Original")
        await user_repository.save(user)

        # Update user data
        user.username = "updated_username"
        user.first_name = "Updated"

        # Save updated user
        updated_user = await user_repository.save(user)

        # Verify update
        assert updated_user.username == "updated_username"
        assert updated_user.first_name == "Updated"

        # Verify in database
        retrieved_user = await user_repository.get_by_id(user.id)
        assert retrieved_user.username == "updated_username"
        assert retrieved_user.first_name == "Updated"

    async def test_block_and_unblock_user(self, user_repository: IUserRepository):
        """Test blocking and unblocking a user."""
        # Create and save user
        user = UserFactory.create(is_blocked=False)
        await user_repository.save(user)

        # Block user
        user.block()
        blocked_user = await user_repository.save(user)

        assert blocked_user.is_blocked is True

        # Verify in database
        retrieved_user = await user_repository.get_by_id(user.id)
        assert retrieved_user.is_blocked is True

        # Unblock user
        user.unblock()
        unblocked_user = await user_repository.save(user)

        assert unblocked_user.is_blocked is False

        # Verify in database
        retrieved_user = await user_repository.get_by_id(user.id)
        assert retrieved_user.is_blocked is False

    async def test_get_blocked_users_empty(self, user_repository: IUserRepository):
        """Test getting blocked users when none exist."""
        blocked_users = await user_repository.get_blocked_users()

        assert blocked_users == []

    async def test_get_blocked_users_with_data(self, user_repository: IUserRepository):
        """Test getting blocked users with mixed data."""
        # Create users - some blocked, some not
        blocked_user1 = UserFactory.create_blocked()
        blocked_user2 = UserFactory.create_blocked()
        normal_user = UserFactory.create(is_blocked=False)

        # Save all users
        await user_repository.save(blocked_user1)
        await user_repository.save(blocked_user2)
        await user_repository.save(normal_user)

        # Get blocked users
        blocked_users = await user_repository.get_blocked_users()

        # Verify results
        assert len(blocked_users) == 2
        blocked_ids = {user.id for user in blocked_users}
        assert blocked_user1.id in blocked_ids
        assert blocked_user2.id in blocked_ids
        assert normal_user.id not in blocked_ids

    async def test_save_user_with_minimal_data(self, user_repository: IUserRepository):
        """Test saving user with minimal required data."""
        user = UserEntity(id=123456789)

        saved_user = await user_repository.save(user)

        assert saved_user.id == 123456789
        assert saved_user.username is None
        assert saved_user.first_name is None
        assert saved_user.last_name is None
        assert saved_user.is_verified is True  # Default
        assert saved_user.is_blocked is False  # Default

    async def test_save_user_with_none_values(self, user_repository: IUserRepository):
        """Test saving user with explicit None values."""
        user = UserFactory.create(username=None, first_name=None, last_name=None)

        saved_user = await user_repository.save(user)

        assert saved_user.username is None
        assert saved_user.first_name is None
        assert saved_user.last_name is None

    async def test_multiple_users_different_ids(self, user_repository: IUserRepository):
        """Test saving multiple users with different IDs."""
        users = UserFactory.create_batch(5)

        # Save all users
        saved_users = []
        for user in users:
            saved_user = await user_repository.save(user)
            saved_users.append(saved_user)

        # Verify all users were saved
        assert len(saved_users) == 5

        # Verify all users can be retrieved
        for original_user in users:
            retrieved_user = await user_repository.get_by_id(original_user.id)
            assert retrieved_user is not None
            assert retrieved_user.id == original_user.id

    async def test_user_state_persistence(self, user_repository: IUserRepository):
        """Test that user state changes persist across saves."""
        user = UserFactory.create(is_verified=True, is_blocked=False)
        await user_repository.save(user)

        # Change user state
        user.is_verified = False
        user.block()

        # Save changes
        await user_repository.save(user)

        # Retrieve and verify
        retrieved_user = await user_repository.get_by_id(user.id)
        assert retrieved_user.is_verified is False
        assert retrieved_user.is_blocked is True


@pytest.mark.integration
class TestUserRepositoryEdgeCases:
    """Edge cases and error conditions for UserRepository."""

    async def test_save_user_with_duplicate_id(self, user_repository: IUserRepository):
        """Test saving users with the same ID (should update)."""
        user_id = 123456789

        # Create first user
        user1 = UserFactory.create(id=user_id, username="user1", first_name="First")
        await user_repository.save(user1)

        # Create second user with same ID but different data
        user2 = UserFactory.create(id=user_id, username="user2", first_name="Second")
        saved_user2 = await user_repository.save(user2)

        # Should have updated the existing user
        assert saved_user2.id == user_id
        assert saved_user2.username == "user2"
        assert saved_user2.first_name == "Second"

        # Verify only one user exists in database
        retrieved_user = await user_repository.get_by_id(user_id)
        assert retrieved_user.username == "user2"
        assert retrieved_user.first_name == "Second"

    async def test_concurrent_user_operations(self, user_repository: IUserRepository):
        """Test operations on multiple different users (sequential due to session limitations)."""
        users = UserFactory.create_batch(10)

        # Save users sequentially (SQLAlchemy session doesn't support true concurrency)
        saved_users = []
        for user in users:
            saved_user = await user_repository.save(user)
            saved_users.append(saved_user)

        assert len(saved_users) == 10

        # Retrieve users sequentially
        retrieved_users = []
        for user in users:
            retrieved_user = await user_repository.get_by_id(user.id)
            retrieved_users.append(retrieved_user)

        assert len(retrieved_users) == 10
        assert all(user is not None for user in retrieved_users)

    async def test_user_with_very_long_strings(self, user_repository: IUserRepository):
        """Test user with very long string values."""
        long_string = "a" * 1000  # Very long string

        user = UserFactory.create(
            username=long_string[:50],  # Assuming reasonable DB limits
            first_name=long_string[:100],
            last_name=long_string[:100],
        )

        saved_user = await user_repository.save(user)

        assert saved_user.username == long_string[:50]
        assert saved_user.first_name == long_string[:100]
        assert saved_user.last_name == long_string[:100]

    async def test_user_with_special_characters(self, user_repository: IUserRepository):
        """Test user with special characters in strings."""
        user = UserFactory.create(
            username="用户名_123",  # Chinese characters + underscore + numbers
            first_name="José",  # Accent character
            last_name="O'Connor",  # Apostrophe
        )

        await user_repository.save(user)
        retrieved_user = await user_repository.get_by_id(user.id)

        assert retrieved_user.username == "用户名_123"
        assert retrieved_user.first_name == "José"
        assert retrieved_user.last_name == "O'Connor"
