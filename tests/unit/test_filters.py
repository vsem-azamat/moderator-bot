"""Tests for telegram filters."""

from unittest.mock import AsyncMock, patch

import pytest
from aiogram import types
from app.presentation.telegram.utils.filters import AdminFilter, ChatTypeFilter, SuperAdminFilter


@pytest.mark.unit
class TestSuperAdminFilter:
    """Test SuperAdminFilter."""

    @pytest.fixture
    def filter_instance(self):
        return SuperAdminFilter()

    @pytest.fixture
    def mock_message(self):
        message = AsyncMock(spec=types.Message)
        message.from_user = AsyncMock()
        return message

    async def test_super_admin_allowed(self, filter_instance, mock_message):
        """Test that super admin is allowed."""
        with patch("app.presentation.telegram.utils.filters.settings") as mock_settings:
            mock_settings.admin.super_admins = [123456789, 987654321]
            mock_message.from_user.id = 123456789

            # Act
            result = await filter_instance(mock_message)

            # Assert
            assert result is True

    async def test_non_super_admin_denied(self, filter_instance, mock_message):
        """Test that non-super admin is denied."""
        with patch("app.presentation.telegram.utils.filters.settings") as mock_settings:
            mock_settings.admin.super_admins = [123456789, 987654321]
            mock_message.from_user.id = 555555555  # Not in super admins

            # Act
            result = await filter_instance(mock_message)

            # Assert
            assert result is False

    async def test_empty_super_admins_list(self, filter_instance, mock_message):
        """Test with empty super admins list."""
        with patch("app.presentation.telegram.utils.filters.settings") as mock_settings:
            mock_settings.admin.super_admins = []
            mock_message.from_user.id = 123456789

            # Act
            result = await filter_instance(mock_message)

            # Assert
            assert result is False


@pytest.mark.unit
class TestAdminFilter:
    """Test AdminFilter."""

    @pytest.fixture
    def filter_instance(self):
        return AdminFilter()

    @pytest.fixture
    def mock_message(self):
        message = AsyncMock(spec=types.Message)
        message.from_user = AsyncMock()
        return message

    @pytest.fixture
    def mock_db_session(self):
        return AsyncMock()

    async def test_admin_allowed(self, filter_instance, mock_message, mock_db_session):
        """Test that admin is allowed."""
        mock_message.from_user.id = 123456789

        with patch("app.presentation.telegram.utils.filters.get_admin_repository") as mock_get_repo:
            mock_repo = AsyncMock()

            # Create mock admin objects
            mock_admin1 = AsyncMock()
            mock_admin1.id = 123456789
            mock_admin2 = AsyncMock()
            mock_admin2.id = 987654321

            mock_repo.get_db_admins.return_value = [mock_admin1, mock_admin2]
            mock_get_repo.return_value = mock_repo

            # Act
            result = await filter_instance(mock_message, mock_db_session)

            # Assert
            assert result is True
            mock_get_repo.assert_called_once_with(mock_db_session)

    async def test_non_admin_denied(self, filter_instance, mock_message, mock_db_session):
        """Test that non-admin is denied."""
        mock_message.from_user.id = 555555555  # Not in admins

        with patch("app.presentation.telegram.utils.filters.get_admin_repository") as mock_get_repo:
            mock_repo = AsyncMock()

            # Create mock admin objects
            mock_admin1 = AsyncMock()
            mock_admin1.id = 123456789
            mock_admin2 = AsyncMock()
            mock_admin2.id = 987654321

            mock_repo.get_db_admins.return_value = [mock_admin1, mock_admin2]
            mock_get_repo.return_value = mock_repo

            # Act
            result = await filter_instance(mock_message, mock_db_session)

            # Assert
            assert result is False

    async def test_empty_admins_list(self, filter_instance, mock_message, mock_db_session):
        """Test with empty admins list."""
        mock_message.from_user.id = 123456789

        with patch("app.presentation.telegram.utils.filters.get_admin_repository") as mock_get_repo:
            mock_repo = AsyncMock()
            mock_repo.get_db_admins.return_value = []
            mock_get_repo.return_value = mock_repo

            # Act
            result = await filter_instance(mock_message, mock_db_session)

            # Assert
            assert result is False


@pytest.mark.unit
class TestChatTypeFilter:
    """Test ChatTypeFilter."""

    @pytest.fixture
    def mock_message(self):
        message = AsyncMock(spec=types.Message)
        message.chat = AsyncMock()
        return message

    async def test_single_chat_type_match(self, mock_message):
        """Test single chat type that matches."""
        # Arrange
        filter_instance = ChatTypeFilter("group")
        mock_message.chat.type = "group"

        # Act
        result = await filter_instance(mock_message)

        # Assert
        assert result is True

    async def test_single_chat_type_no_match(self, mock_message):
        """Test single chat type that doesn't match."""
        # Arrange
        filter_instance = ChatTypeFilter("group")
        mock_message.chat.type = "private"

        # Act
        result = await filter_instance(mock_message)

        # Assert
        assert result is False

    async def test_multiple_chat_types_match(self, mock_message):
        """Test multiple chat types with match."""
        # Arrange
        filter_instance = ChatTypeFilter(["group", "supergroup"])
        mock_message.chat.type = "supergroup"

        # Act
        result = await filter_instance(mock_message)

        # Assert
        assert result is True

    async def test_multiple_chat_types_no_match(self, mock_message):
        """Test multiple chat types with no match."""
        # Arrange
        filter_instance = ChatTypeFilter(["group", "supergroup"])
        mock_message.chat.type = "private"

        # Act
        result = await filter_instance(mock_message)

        # Assert
        assert result is False

    async def test_empty_chat_types_list(self, mock_message):
        """Test empty chat types list."""
        # Arrange
        filter_instance = ChatTypeFilter([])
        mock_message.chat.type = "group"

        # Act
        result = await filter_instance(mock_message)

        # Assert
        assert result is False

    def test_filter_initialization_string(self):
        """Test filter initialization with string."""
        filter_instance = ChatTypeFilter("private")
        assert filter_instance.chat_type == "private"

    def test_filter_initialization_list(self):
        """Test filter initialization with list."""
        chat_types = ["group", "supergroup"]
        filter_instance = ChatTypeFilter(chat_types)
        assert filter_instance.chat_type == chat_types

    async def test_case_sensitive_matching(self, mock_message):
        """Test that chat type matching is case sensitive."""
        # Arrange
        filter_instance = ChatTypeFilter("GROUP")  # Uppercase
        mock_message.chat.type = "group"  # Lowercase

        # Act
        result = await filter_instance(mock_message)

        # Assert
        assert result is False


@pytest.mark.unit
class TestFilterIntegration:
    """Integration tests for filters."""

    @pytest.fixture
    def mock_message(self):
        message = AsyncMock(spec=types.Message)
        message.from_user = AsyncMock()
        message.chat = AsyncMock()
        return message

    async def test_filters_work_independently(self, mock_message):
        """Test that different filters work independently."""
        # Setup message
        mock_message.from_user.id = 123456789
        mock_message.chat.type = "group"

        # Test SuperAdminFilter
        super_admin_filter = SuperAdminFilter()
        with patch("app.presentation.telegram.utils.filters.settings") as mock_settings:
            mock_settings.admin.super_admins = [123456789]
            super_admin_result = await super_admin_filter(mock_message)
            assert super_admin_result is True

        # Test ChatTypeFilter
        chat_type_filter = ChatTypeFilter("group")
        chat_type_result = await chat_type_filter(mock_message)
        assert chat_type_result is True

        # Test different chat type
        chat_type_filter_private = ChatTypeFilter("private")
        chat_type_result_private = await chat_type_filter_private(mock_message)
        assert chat_type_result_private is False

    async def test_multiple_filter_combinations(self, mock_message):
        """Test multiple filter combinations."""
        mock_message.from_user.id = 123456789
        mock_message.chat.type = "supergroup"

        # Test combinations
        filters_and_expected = [
            (SuperAdminFilter(), [123456789], True),
            (SuperAdminFilter(), [987654321], False),
            (ChatTypeFilter("supergroup"), None, True),
            (ChatTypeFilter("private"), None, False),
            (ChatTypeFilter(["group", "supergroup"]), None, True),
            (ChatTypeFilter(["private", "channel"]), None, False),
        ]

        for filter_instance, super_admins, expected in filters_and_expected:
            if isinstance(filter_instance, SuperAdminFilter):
                with patch("app.presentation.telegram.utils.filters.settings") as mock_settings:
                    mock_settings.admin.super_admins = super_admins
                    result = await filter_instance(mock_message)
                    assert result == expected, f"Failed for {filter_instance.__class__.__name__} with {super_admins}"
            else:
                result = await filter_instance(mock_message)
                assert result == expected, (
                    f"Failed for {filter_instance.__class__.__name__} with {filter_instance.chat_type}"
                )
