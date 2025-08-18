"""Chat management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.chat import ChatRepository
from app.infrastructure.db.session import get_db_session
from app.presentation.api.schemas.chat import ChatResponse, ChatStatsResponse, ChatUpdateRequest

router = APIRouter()


async def get_chat_repository(db: AsyncSession = Depends(get_db_session)) -> ChatRepository:
    """Get chat repository dependency."""
    return ChatRepository(db)


@router.get("", response_model=list[ChatResponse])
async def get_all_chats(chat_repo: ChatRepository = Depends(get_chat_repository)) -> list[ChatResponse]:
    """Get all chats with their configurations."""
    try:
        chats = await chat_repo.get_all()
        return [ChatResponse.from_entity(chat) for chat in chats]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chats: {str(e)}") from None


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(chat_id: int, chat_repo: ChatRepository = Depends(get_chat_repository)) -> ChatResponse:
    """Get specific chat by ID."""
    try:
        chat = await chat_repo.get_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return ChatResponse.from_entity(chat)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat: {str(e)}") from None


@router.put("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: int, update_data: ChatUpdateRequest, chat_repo: ChatRepository = Depends(get_chat_repository)
) -> ChatResponse:
    """Update chat configuration."""
    try:
        chat = await chat_repo.get_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Update chat properties
        if update_data.welcome_message is not None:
            chat.welcome_message = update_data.welcome_message
        if update_data.welcome_delete_time is not None:
            chat.set_welcome_delete_time(update_data.welcome_delete_time)
        if update_data.is_welcome_enabled is not None:
            if update_data.is_welcome_enabled:
                chat.enable_welcome()
            else:
                chat.disable_welcome()
        if update_data.is_captcha_enabled is not None:
            if update_data.is_captcha_enabled:
                chat.enable_captcha()
            else:
                chat.disable_captcha()

        updated_chat = await chat_repo.save(chat)
        return ChatResponse.from_entity(updated_chat)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update chat: {str(e)}") from None


@router.get("/{chat_id}/stats", response_model=ChatStatsResponse)
async def get_chat_stats(chat_id: int, chat_repo: ChatRepository = Depends(get_chat_repository)) -> ChatStatsResponse:
    """Get chat statistics and analytics."""
    try:
        chat = await chat_repo.get_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # TODO: Implement actual statistics gathering
        # For now, return mock data
        return ChatStatsResponse(
            chat_id=chat_id,
            member_count=0,  # TODO: Get from Telegram API
            message_count_24h=0,  # TODO: Get from message repository
            active_users_24h=0,  # TODO: Calculate from messages
            moderation_actions_24h=0,  # TODO: Get from logs
            last_activity=None,  # TODO: Get from messages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat stats: {str(e)}") from None


@router.post("/bulk-update", response_model=list[ChatResponse])
async def bulk_update_chats(
    chat_ids: list[int], update_data: ChatUpdateRequest, chat_repo: ChatRepository = Depends(get_chat_repository)
) -> list[ChatResponse]:
    """Perform bulk operations on multiple chats."""
    try:
        updated_chats = []

        for chat_id in chat_ids:
            chat = await chat_repo.get_by_id(chat_id)
            if not chat:
                continue  # Skip non-existent chats

            # Apply updates
            if update_data.welcome_message is not None:
                chat.welcome_message = update_data.welcome_message
            if update_data.welcome_delete_time is not None:
                chat.set_welcome_delete_time(update_data.welcome_delete_time)
            if update_data.is_welcome_enabled is not None:
                if update_data.is_welcome_enabled:
                    chat.enable_welcome()
                else:
                    chat.disable_welcome()
            if update_data.is_captcha_enabled is not None:
                if update_data.is_captcha_enabled:
                    chat.enable_captcha()
                else:
                    chat.disable_captcha()

            updated_chat = await chat_repo.save(chat)
            updated_chats.append(ChatResponse.from_entity(updated_chat))

        return updated_chats
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to bulk update chats: {str(e)}") from None
