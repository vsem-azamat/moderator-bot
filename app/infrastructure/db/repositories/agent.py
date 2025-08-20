from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.agent import AgentSession, ModelProvider, OpenRouterModel
from app.domain.repositories import IAgentRepository


class InMemoryAgentRepository(IAgentRepository):
    """In-memory реализация репозитория агента для развертывания без БД."""

    def __init__(self) -> None:
        self._sessions: dict[str, AgentSession] = {}

    async def save_session(self, session: AgentSession) -> AgentSession:
        """Save agent session."""
        self._sessions[session.id] = session
        return session

    async def get_session(self, session_id: str) -> AgentSession | None:
        """Get agent session by ID."""
        return self._sessions.get(session_id)

    async def get_user_sessions(self, user_id: int, limit: int = 20) -> list[AgentSession]:
        """Get user's agent sessions."""
        user_sessions = [
            session for session in self._sessions.values() if session.user_id.value == user_id and session.is_active
        ]
        # Сортируем по времени обновления (новые сначала)
        user_sessions.sort(key=lambda x: x.updated_at, reverse=True)
        return user_sessions[:limit]

    async def delete_session(self, session_id: str) -> bool:
        """Delete agent session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    async def update_session(self, session: AgentSession) -> AgentSession:
        """Update agent session."""
        if session.id in self._sessions:
            self._sessions[session.id] = session
            return session
        raise ValueError(f"Session {session.id} not found")

    async def get_available_models(self, provider: ModelProvider) -> list[OpenRouterModel]:
        """Get available models for provider."""
        if provider == ModelProvider.OPENAI:
            return [
                OpenRouterModel(
                    id="gpt-4o",
                    name="GPT-4o",
                    description="Новейшая модель OpenAI с мультимодальными возможностями",
                    context_length=128000,
                ),
                OpenRouterModel(
                    id="gpt-4o-mini",
                    name="GPT-4o Mini",
                    description="Быстрая и экономичная версия GPT-4o",
                    context_length=128000,
                ),
                OpenRouterModel(
                    id="gpt-4-turbo",
                    name="GPT-4 Turbo",
                    description="Улучшенная версия GPT-4 с увеличенным контекстом",
                    context_length=128000,
                ),
            ]
        # provider == ModelProvider.OPENROUTER
        return [
            OpenRouterModel(
                id="anthropic/claude-3.5-sonnet",
                name="Claude 3.5 Sonnet",
                description="Лучший баланс интеллекта и скорости от Anthropic",
                context_length=200000,
            ),
            OpenRouterModel(
                id="google/gemini-pro-1.5",
                name="Gemini Pro 1.5",
                description="Продвинутая модель Google с большим контекстом",
                context_length=1000000,
            ),
            OpenRouterModel(
                id="meta-llama/llama-3.1-70b-instruct",
                name="Llama 3.1 70B",
                description="Открытая модель Meta с высокой производительностью",
                context_length=131072,
            ),
            OpenRouterModel(
                id="mistralai/mixtral-8x7b-instruct",
                name="Mixtral 8x7B",
                description="Эффективная модель смеси экспертов от Mistral AI",
                context_length=32768,
            ),
        ]


# TODO: Полная реализация с PostgreSQL будет добавлена позже
class SQLAgentRepository(IAgentRepository):
    """SQL-based реализация репозитория агента (планируется)."""

    def __init__(self, session: AsyncSession):
        self.session = session
        # Пока используем in-memory как fallback
        self._fallback = InMemoryAgentRepository()

    async def save_session(self, session: AgentSession) -> AgentSession:
        return await self._fallback.save_session(session)

    async def get_session(self, session_id: str) -> AgentSession | None:
        return await self._fallback.get_session(session_id)

    async def get_user_sessions(self, user_id: int, limit: int = 20) -> list[AgentSession]:
        return await self._fallback.get_user_sessions(user_id, limit)

    async def delete_session(self, session_id: str) -> bool:
        return await self._fallback.delete_session(session_id)

    async def update_session(self, session: AgentSession) -> AgentSession:
        return await self._fallback.update_session(session)

    async def get_available_models(self, provider: ModelProvider) -> list[OpenRouterModel]:
        return await self._fallback.get_available_models(provider)
