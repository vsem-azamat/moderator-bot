from fastapi import APIRouter, Depends, HTTPException

from app.application.services.agent_service import AgentService
from app.core.container import get_container
from app.domain.agent import AgentModelConfig, ModelProvider
from app.presentation.api.schemas.agent import (
    AgentResponseSchema,
    ChatMessageRequest,
    CreateSessionRequest,
    ModelConfigSchema,
    SessionResponse,
)

router = APIRouter()


def get_agent_service() -> AgentService:
    """Get agent service dependency."""
    container = get_container()
    return container.get_agent_service()


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest, agent_service: AgentService = Depends(get_agent_service)
) -> SessionResponse:
    """Create a new agent session."""
    try:
        # Convert schema to domain model
        model_config = AgentModelConfig(
            provider=request.agent_config.provider,
            model_id=request.agent_config.model_id,
            model_name=request.agent_config.model_name,
            api_key_env="OPENAI_API_KEY",  # Default for now
            temperature=request.agent_config.temperature,
            max_tokens=request.agent_config.max_tokens,
        )

        # For now, use a dummy user_id
        user_id = 1

        session = await agent_service.create_session(user_id=user_id, model_config=model_config, title=request.title)

        return SessionResponse(
            id=session.id,
            title=session.title,
            agent_config=ModelConfigSchema.from_domain(session.agent_config),
            system_prompt=session.system_prompt,
            created_at=session.created_at,
            updated_at=session.updated_at,
            is_active=session.is_active,
            message_count=len(session.messages),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(agent_service: AgentService = Depends(get_agent_service)) -> list[SessionResponse]:
    """List all sessions for the current user."""
    try:
        # For now, use a dummy user_id
        user_id = 1

        sessions = await agent_service.get_user_sessions(user_id, limit=20)

        return [
            SessionResponse(
                id=session.id,
                title=session.title,
                agent_config=ModelConfigSchema.from_domain(session.agent_config),
                system_prompt=session.system_prompt,
                created_at=session.created_at,
                updated_at=session.updated_at,
                is_active=session.is_active,
                message_count=len(session.messages),
            )
            for session in sessions
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, agent_service: AgentService = Depends(get_agent_service)) -> SessionResponse:
    """Get a specific session."""
    try:
        session = await agent_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionResponse(
            id=session.id,
            title=session.title,
            agent_config=ModelConfigSchema.from_domain(session.agent_config),
            system_prompt=session.system_prompt,
            created_at=session.created_at,
            updated_at=session.updated_at,
            is_active=session.is_active,
            message_count=len(session.messages),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/sessions/{session_id}/chat", response_model=AgentResponseSchema)
async def chat_with_agent(
    session_id: str, request: ChatMessageRequest, agent_service: AgentService = Depends(get_agent_service)
) -> AgentResponseSchema:
    """Send a message to the agent and get a response."""
    try:
        response = await agent_service.chat(session_id, request.message)

        return AgentResponseSchema(
            session_id=response.session_id,
            message=response.message,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            execution_time=response.execution_time,
            timestamp=response.timestamp,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, agent_service: AgentService = Depends(get_agent_service)) -> dict[str, str]:
    """Delete a session."""
    try:
        success = await agent_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"message": "Session deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/models", response_model=list[ModelConfigSchema])
async def list_available_models() -> list[ModelConfigSchema]:
    """List available AI models."""
    # Return some common models for now
    return [
        ModelConfigSchema(
            provider=ModelProvider.OPENAI,
            model_id="gpt-4o-mini",
            model_name="GPT-4o Mini",
            temperature=0.7,
            max_tokens=2000,
        ),
        ModelConfigSchema(
            provider=ModelProvider.OPENAI, model_id="gpt-4o", model_name="GPT-4o", temperature=0.7, max_tokens=4000
        ),
        ModelConfigSchema(
            provider=ModelProvider.OPENROUTER,
            model_id="anthropic/claude-3-5-sonnet",
            model_name="Claude 3.5 Sonnet",
            temperature=0.7,
            max_tokens=4000,
        ),
    ]
