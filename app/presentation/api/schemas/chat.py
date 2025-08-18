"""Chat API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.entities import ChatEntity


class ChatResponse(BaseModel):
    """Chat response schema."""

    id: int
    title: str | None = None
    is_forum: bool = False
    welcome_message: str | None = None
    welcome_delete_time: int = 60
    is_welcome_enabled: bool = False
    is_captcha_enabled: bool = False
    created_at: datetime | None = None
    modified_at: datetime | None = None

    @classmethod
    def from_entity(cls, entity: ChatEntity) -> "ChatResponse":
        """Create response from chat entity."""
        return cls(
            id=entity.id,
            title=entity.title,
            # Handle None values from database for is_forum field
            is_forum=entity.is_forum if entity.is_forum is not None else False,
            welcome_message=entity.welcome_message,
            welcome_delete_time=entity.welcome_delete_time,
            is_welcome_enabled=entity.is_welcome_enabled,
            is_captcha_enabled=entity.is_captcha_enabled,
            created_at=entity.created_at,
            modified_at=entity.modified_at,
        )


class ChatUpdateRequest(BaseModel):
    """Chat update request schema."""

    welcome_message: str | None = None
    welcome_delete_time: int | None = Field(None, gt=0, description="Auto-delete time in seconds")
    is_welcome_enabled: bool | None = None
    is_captcha_enabled: bool | None = None


class ChatStatsResponse(BaseModel):
    """Chat statistics response schema."""

    chat_id: int
    member_count: int
    message_count_24h: int
    active_users_24h: int
    moderation_actions_24h: int
    last_activity: datetime | None = None


class BulkUpdateRequest(BaseModel):
    """Bulk update request schema."""

    chat_ids: list[int]
    update_data: ChatUpdateRequest
