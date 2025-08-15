"""Domain exceptions for the moderation bot."""
# ruff: noqa: N818


class DomainError(Exception):
    """Base domain exception."""

    pass


class UserNotFoundException(DomainError):
    """Raised when user is not found."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")


class ChatNotFoundException(DomainError):
    """Raised when chat is not found."""

    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        super().__init__(f"Chat with ID {chat_id} not found")


class AdminNotFoundException(DomainError):
    """Raised when admin is not found."""

    def __init__(self, admin_id: int):
        self.admin_id = admin_id
        super().__init__(f"Admin with ID {admin_id} not found")


class UserAlreadyBlockedException(DomainError):
    """Raised when trying to block an already blocked user."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User {user_id} is already blocked")


class UserNotBlockedException(DomainError):
    """Raised when trying to unblock a user that isn't blocked."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User {user_id} is not blocked")


class AdminAlreadyExistsException(DomainError):
    """Raised when trying to add an existing admin."""

    def __init__(self, admin_id: int):
        self.admin_id = admin_id
        super().__init__(f"Admin {admin_id} already exists")


class InsufficientPermissionsException(DomainError):
    """Raised when user lacks required permissions."""

    def __init__(self, user_id: int, action: str):
        self.user_id = user_id
        self.action = action
        super().__init__(f"User {user_id} lacks permissions for action: {action}")


class InvalidModerationTargetException(DomainError):
    """Raised when trying to moderate an invalid target."""

    def __init__(self, message: str):
        super().__init__(message)


class TelegramApiException(DomainError):
    """Raised when Telegram API operation fails."""

    def __init__(self, operation: str, error: str):
        self.operation = operation
        self.error = error
        super().__init__(f"Telegram API error during {operation}: {error}")


class ConfigurationException(DomainError):
    """Raised when there's a configuration error."""

    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")


class ValidationException(DomainError):
    """Raised when validation fails."""

    def __init__(self, field: str, value: any, message: str):
        self.field = field
        self.value = value
        super().__init__(f"Validation error for {field}='{value}': {message}")
