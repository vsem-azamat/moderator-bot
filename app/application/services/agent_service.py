import time
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.application.services.agent_tools import AgentTools, ChatInfo
from app.core.logging import BotLogger
from app.domain.agent import AgentModelConfig, AgentResponse, AgentSession, AgentToolResult, ModelProvider
from app.domain.repositories import IAgentRepository, IChatRepository, IUserRepository
from app.domain.value_objects import UserId


class AgentContext(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    user_id: int
    session_id: str
    tools: AgentTools


class AgentService:
    def __init__(
        self,
        agent_repository: IAgentRepository,
        chat_repository: IChatRepository,
        user_repository: IUserRepository,
        logger: BotLogger,
    ) -> None:
        self.agent_repository = agent_repository
        self.chat_repository = chat_repository
        self.user_repository = user_repository
        self.logger = logger

        self.tools = AgentTools(chat_repository, user_repository, logger)
        self._agents: dict[str, Agent[AgentContext]] = {}

    def _create_agent(self, model_config: AgentModelConfig) -> Agent[AgentContext]:
        """Создать PydanticAI агента с указанной конфигурацией модели."""

        # Определяем модель в зависимости от провайдера
        if model_config.provider == ModelProvider.OPENAI:
            model = model_config.model_id
        elif model_config.provider == ModelProvider.OPENROUTER:
            # OpenRouter использует OpenAI-совместимый API
            model = f"openai:{model_config.model_id}"
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {model_config.provider}")

        # Системный промпт для управления чатами
        system_prompt = """
Ты - AI помощник для управления Telegram чатами и каналами модераторского бота.
Твоя цель - помочь администраторам эффективно управлять сообществами.

Основные возможности:
- Получение списка всех чатов и их детальной информации
- Обновление описаний чатов и настроек приветствий
- Поиск чатов по названию или описанию
- Анализ статистики по чатам и пользователям

Всегда отвечай на русском языке профессионально и конструктивно.
При выполнении операций всегда сообщай о результате.
Если произошла ошибка, объясни что пошло не так и предложи альтернативы.
"""

        agent = Agent(
            model,
            deps_type=AgentContext,
            system_prompt=system_prompt,
            model_settings={
                "temperature": model_config.temperature,
                "max_tokens": model_config.max_tokens or 2000,
            },
        )

        # Регистрируем tools
        @agent.tool
        async def get_all_chats(ctx: RunContext[AgentContext]) -> list[ChatInfo]:
            """Получить список всех управляемых чатов с основной информацией."""
            return await ctx.deps.tools.get_all_chats()

        @agent.tool
        async def get_chat_details(ctx: RunContext[AgentContext], chat_id: int) -> ChatInfo | None:
            """Получить детальную информацию о конкретном чате по его ID."""
            return await ctx.deps.tools.get_chat_details(chat_id)

        @agent.tool
        async def update_chat_description(ctx: RunContext[AgentContext], chat_id: int, description: str) -> bool:
            """Обновить описание чата. Возвращает True если успешно."""
            return await ctx.deps.tools.update_chat_description(chat_id, description)

        @agent.tool
        async def update_chat_settings(
            ctx: RunContext[AgentContext],
            chat_id: int,
            title: str | None = None,
            welcome_text: str | None = None,
            welcome_enabled: bool | None = None,
            auto_delete_time: int | None = None,
        ) -> bool:
            """Обновить настройки чата (описание, приветствие, автоудаление). Возвращает True если успешно."""
            return await ctx.deps.tools.update_chat_settings(
                chat_id, title, welcome_text, welcome_enabled, auto_delete_time
            )

        @agent.tool
        async def get_chat_statistics(ctx: RunContext[AgentContext]) -> dict[str, Any]:
            """Получить общую статистику по всем чатам."""
            return await ctx.deps.tools.get_chat_statistics()

        @agent.tool
        async def search_chats(ctx: RunContext[AgentContext], query: str) -> list[ChatInfo]:
            """Найти чаты по названию или описанию."""
            return await ctx.deps.tools.search_chats(query)

        return agent

    async def create_session(
        self, user_id: int, model_config: AgentModelConfig, title: str | None = None, system_prompt: str | None = None
    ) -> AgentSession:
        """Создать новую сессию с AI агентом."""
        session = AgentSession(
            user_id=UserId(user_id), agent_config=model_config, system_prompt=system_prompt, title=title
        )

        saved_session = await self.agent_repository.save_session(session)
        self.logger.logger.info(f"Создана новая сессия {saved_session.id} для пользователя {user_id}")

        return saved_session

    async def get_session(self, session_id: str) -> AgentSession | None:
        """Получить сессию по ID."""
        return await self.agent_repository.get_session(session_id)

    async def get_user_sessions(self, user_id: int, limit: int = 20) -> list[AgentSession]:
        """Получить сессии пользователя."""
        return await self.agent_repository.get_user_sessions(user_id, limit)

    async def chat(self, session_id: str, message: str) -> AgentResponse:
        """Отправить сообщение агенту и получить ответ."""
        start_time = time.time()

        try:
            # Получаем сессию
            session = await self.agent_repository.get_session(session_id)
            if not session:
                raise ValueError(f"Сессия {session_id} не найдена")

            # Создаем или получаем агента для данной конфигурации
            agent_key = f"{session.agent_config.provider}_{session.agent_config.model_id}"
            if agent_key not in self._agents:
                self._agents[agent_key] = self._create_agent(session.agent_config)

            agent = self._agents[agent_key]

            # Добавляем сообщение пользователя в сессию
            session.add_message("user", message)

            # Подготавливаем контекст
            context = AgentContext(user_id=session.user_id.value, session_id=session_id, tools=self.tools)

            # Выполняем запрос к агенту (упрощенно, без истории сообщений)
            result = await agent.run(user_prompt=message, deps=context)

            # Добавляем ответ агента в сессию
            session.add_message("assistant", str(result))

            # Обновляем сессию в репозитории
            await self.agent_repository.update_session(session)

            # Подготавливаем tool results (упрощенно)
            tool_results: list[AgentToolResult] = []

            execution_time = time.time() - start_time

            response = AgentResponse(
                session_id=session_id,
                message=str(result),
                tool_results=tool_results,
                model_used=f"{session.agent_config.provider}:{session.agent_config.model_id}",
                tokens_used=getattr(result, "usage", {}).get("total_tokens", None)
                if hasattr(result, "usage")
                else None,
                execution_time=execution_time,
            )

            self.logger.logger.info(
                f"Обработан запрос для сессии {session_id}, время выполнения: {execution_time:.2f}с"
            )
            return response

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.logger.error(f"Ошибка при обработке запроса для сессии {session_id}: {e}")

            return AgentResponse(
                session_id=session_id,
                message=f"Произошла ошибка при обработке запроса: {str(e)}",
                model_used="error",
                execution_time=execution_time,
            )

    async def delete_session(self, session_id: str) -> bool:
        """Удалить сессию."""
        success = await self.agent_repository.delete_session(session_id)
        if success:
            self.logger.logger.info(f"Удалена сессия {session_id}")
        return success

    async def get_available_openrouter_models(self) -> list[dict[str, Any]]:
        """Получить список доступных моделей OpenRouter."""
        # TODO: Реализовать запрос к OpenRouter API для получения актуального списка моделей
        # Пока возвращаем статичный список популярных моделей
        return [
            {
                "id": "anthropic/claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "description": "Лучший баланс интеллекта и скорости от Anthropic",
                "context_length": 200000,
            },
            {
                "id": "openai/gpt-4o",
                "name": "GPT-4o",
                "description": "Новейшая модель OpenAI с мультимодальными возможностями",
                "context_length": 128000,
            },
            {
                "id": "google/gemini-pro-1.5",
                "name": "Gemini Pro 1.5",
                "description": "Продвинутая модель Google с большим контекстом",
                "context_length": 1000000,
            },
            {
                "id": "meta-llama/llama-3.1-70b-instruct",
                "name": "Llama 3.1 70B",
                "description": "Открытая модель Meta с высокой производительностью",
                "context_length": 131072,
            },
            {
                "id": "mistralai/mixtral-8x7b-instruct",
                "name": "Mixtral 8x7B",
                "description": "Эффективная модель смеси экспертов от Mistral AI",
                "context_length": 32768,
            },
        ]
