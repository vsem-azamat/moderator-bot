"""Tests for domain exceptions."""

import pytest
from app.domain.exceptions import (
    AdminNotFoundException,
    ChatNotFoundException,
    DomainError,
    UserAlreadyBlockedException,
    UserNotBlockedException,
    UserNotFoundException,
)


@pytest.mark.unit
class TestDomainExceptions:
    """Test domain exceptions."""

    def test_domain_error_base_exception(self):
        """Test DomainError base exception."""
        # Act
        exception = DomainError("Base error message")

        # Assert
        assert str(exception) == "Base error message"
        assert isinstance(exception, Exception)

    def test_domain_error_inheritance(self):
        """Test that all domain exceptions inherit from DomainError."""
        exceptions = [
            UserNotFoundException(123),
            ChatNotFoundException(-456),
            AdminNotFoundException(789),
            UserAlreadyBlockedException(111),
            UserNotBlockedException(222),
        ]

        for exception in exceptions:
            assert isinstance(exception, DomainError)
            assert isinstance(exception, Exception)

    def test_user_not_found_exception(self):
        """Test UserNotFoundException."""
        # Arrange
        user_id = 123456789

        # Act
        exception = UserNotFoundException(user_id)

        # Assert
        assert exception.user_id == user_id
        assert str(exception) == f"User with ID {user_id} not found"

    def test_chat_not_found_exception(self):
        """Test ChatNotFoundException."""
        # Arrange
        chat_id = -1001234567890

        # Act
        exception = ChatNotFoundException(chat_id)

        # Assert
        assert exception.chat_id == chat_id
        assert str(exception) == f"Chat with ID {chat_id} not found"

    def test_admin_not_found_exception(self):
        """Test AdminNotFoundException."""
        # Arrange
        admin_id = 987654321

        # Act
        exception = AdminNotFoundException(admin_id)

        # Assert
        assert exception.admin_id == admin_id
        assert str(exception) == f"Admin with ID {admin_id} not found"

    def test_user_already_blocked_exception(self):
        """Test UserAlreadyBlockedException."""
        # Arrange
        user_id = 555555555

        # Act
        exception = UserAlreadyBlockedException(user_id)

        # Assert
        assert exception.user_id == user_id
        assert str(exception) == f"User {user_id} is already blocked"

    def test_user_not_blocked_exception(self):
        """Test UserNotBlockedException."""
        # Arrange
        user_id = 777777777

        # Act
        exception = UserNotBlockedException(user_id)

        # Assert
        assert exception.user_id == user_id
        assert str(exception) == f"User {user_id} is not blocked"

    def test_exceptions_can_be_raised_and_caught(self):
        """Test that exceptions can be raised and caught properly."""
        # Test UserNotFoundException
        with pytest.raises(UserNotFoundException) as exc_info:
            raise UserNotFoundException(123)
        assert exc_info.value.user_id == 123

        # Test ChatNotFoundException
        with pytest.raises(ChatNotFoundException) as exc_info:
            raise ChatNotFoundException(-456)
        assert exc_info.value.chat_id == -456

        # Test AdminNotFoundException
        with pytest.raises(AdminNotFoundException) as exc_info:
            raise AdminNotFoundException(789)
        assert exc_info.value.admin_id == 789

        # Test UserAlreadyBlockedException
        with pytest.raises(UserAlreadyBlockedException) as exc_info:
            raise UserAlreadyBlockedException(111)
        assert exc_info.value.user_id == 111

        # Test UserNotBlockedException
        with pytest.raises(UserNotBlockedException) as exc_info:
            raise UserNotBlockedException(222)
        assert exc_info.value.user_id == 222

    def test_exceptions_can_be_caught_as_domain_error(self):
        """Test that all domain exceptions can be caught as DomainError."""
        exceptions = [
            UserNotFoundException(123),
            ChatNotFoundException(-456),
            AdminNotFoundException(789),
            UserAlreadyBlockedException(111),
            UserNotBlockedException(222),
        ]

        for exception in exceptions:
            with pytest.raises(DomainError):
                raise exception

    def test_exception_attributes_are_accessible(self):
        """Test that exception attributes are accessible after raising."""
        # Test with pytest.raises to verify attributes are preserved
        with pytest.raises(UserNotFoundException) as exc_info:
            raise UserNotFoundException(12345)
        assert exc_info.value.user_id == 12345
        assert "12345" in str(exc_info.value)

        with pytest.raises(ChatNotFoundException) as exc_info:
            raise ChatNotFoundException(-98765)
        assert exc_info.value.chat_id == -98765
        assert "-98765" in str(exc_info.value)

        with pytest.raises(AdminNotFoundException) as exc_info:
            raise AdminNotFoundException(54321)
        assert exc_info.value.admin_id == 54321
        assert "54321" in str(exc_info.value)

    def test_negative_user_ids(self):
        """Test exceptions with negative user IDs."""
        # Some Telegram bots might use negative IDs
        negative_user_id = -123456

        exception = UserNotFoundException(negative_user_id)
        assert exception.user_id == negative_user_id
        assert str(negative_user_id) in str(exception)

    def test_zero_ids(self):
        """Test exceptions with zero IDs."""
        zero_id = 0

        # Test all ID-based exceptions with zero
        exceptions = [
            UserNotFoundException(zero_id),
            ChatNotFoundException(zero_id),
            AdminNotFoundException(zero_id),
            UserAlreadyBlockedException(zero_id),
            UserNotBlockedException(zero_id),
        ]

        for exception in exceptions:
            assert "0" in str(exception)

    def test_large_ids(self):
        """Test exceptions with large IDs."""
        large_id = 999999999999999

        exception = UserNotFoundException(large_id)
        assert exception.user_id == large_id
        assert str(large_id) in str(exception)


@pytest.mark.unit
class TestExceptionChaining:
    """Test exception chaining and context."""

    def test_exception_can_be_chained(self):
        """Test that domain exceptions can be chained with other exceptions."""
        original_error = ValueError("Original error")
        with pytest.raises(UserNotFoundException) as exc_info:
            raise UserNotFoundException(123) from original_error
        assert exc_info.value.user_id == 123
        assert isinstance(exc_info.value.__cause__, ValueError)
        assert str(exc_info.value.__cause__) == "Original error"

    def test_exception_context_preservation(self):
        """Test that exception context can be suppressed."""
        with pytest.raises(ChatNotFoundException) as exc_info:
            raise ChatNotFoundException(-123)
        assert exc_info.value.chat_id == -123
