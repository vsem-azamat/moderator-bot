from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.domain.value_objects import UserId


class ModelProvider(str, Enum):
    OPENAI = "openai"
    OPENROUTER = "openrouter"


class OpenRouterModel(BaseModel):
    id: str
    name: str
    description: str | None = None
    pricing: dict[str, float] = Field(default_factory=dict)
    context_length: int | None = None
    architecture: str | None = None
    modality: str = "text"


class AgentModelConfig(BaseModel):
    provider: ModelProvider
    model_id: str
    model_name: str | None = None
    api_key: str | None = None  # API key will be injected at runtime
    base_url: str | None = None
    max_tokens: int | None = None
    temperature: float = 0.7


class AgentMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: UserId
    title: str | None = None
    messages: list[AgentMessage] = Field(default_factory=list)
    agent_config: AgentModelConfig
    system_prompt: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_message(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> AgentMessage:
        message = AgentMessage(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        return message

    def get_conversation_history(self, limit: int | None = None) -> list[dict[str, Any]]:
        messages = self.messages[-limit:] if limit else self.messages
        return [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat()} for msg in messages]


class AgentToolResult(BaseModel):
    tool_name: str
    success: bool
    result: Any
    error: str | None = None
    execution_time: float | None = None


class AgentResponse(BaseModel):
    session_id: str
    message: str
    tool_results: list[AgentToolResult] = Field(default_factory=list)
    model_used: str
    tokens_used: int | None = None
    execution_time: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
