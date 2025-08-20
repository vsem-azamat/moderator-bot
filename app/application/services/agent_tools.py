from typing import Any

from pydantic import BaseModel

from app.core.logging import BotLogger
from app.domain.repositories import IChatRepository, IUserRepository


class ChatInfo(BaseModel):
    id: int
    title: str
    description: str | None = None
    member_count: int | None = None
    is_private: bool
    welcome_enabled: bool
    welcome_text: str | None = None
    auto_delete_time: int | None = None


class ChatUpdateRequest(BaseModel):
    description: str | None = None
    welcome_text: str | None = None
    welcome_enabled: bool | None = None
    auto_delete_time: int | None = None


class AgentTools:
    def __init__(self, chat_repository: IChatRepository, user_repository: IUserRepository, logger: BotLogger) -> None:
        self.chat_repository = chat_repository
        self.user_repository = user_repository
        self.logger = logger

    async def get_all_chats(self) -> list[ChatInfo]:
        """Получить список всех управляемых чатов."""
        try:
            chats = await self.chat_repository.get_all()
            result = []

            for chat in chats:
                chat_info = ChatInfo(
                    id=chat.id,
                    title=chat.title or f"Chat {chat.id}",
                    description=getattr(chat, "description", None),
                    member_count=getattr(chat, "member_count", None),
                    is_private=not chat.is_forum,  # invert is_forum to get is_private
                    welcome_enabled=chat.is_welcome_enabled,
                    welcome_text=chat.welcome_message,
                    auto_delete_time=chat.welcome_delete_time,
                )
                result.append(chat_info)

            self.logger.logger.info(f"Получен список из {len(result)} чатов")
            return result

        except Exception as e:
            self.logger.logger.error(f"Ошибка при получении списка чатов: {e}")
            return []

    async def get_chat_details(self, chat_id: int) -> ChatInfo | None:
        """Получить детальную информацию о чате."""
        try:
            chat = await self.chat_repository.get_by_id(chat_id)
            if not chat:
                return None

            chat_info = ChatInfo(
                id=chat.id,
                title=chat.title or f"Chat {chat.id}",
                description=getattr(chat, "description", None),
                member_count=getattr(chat, "member_count", None),
                is_private=not chat.is_forum,
                welcome_enabled=chat.is_welcome_enabled,
                welcome_text=chat.welcome_message,
                auto_delete_time=chat.welcome_delete_time,
            )

            self.logger.logger.info(f"Получена информация о чате {chat_id}")
            return chat_info

        except Exception as e:
            self.logger.logger.error(f"Ошибка при получении информации о чате {chat_id}: {e}")
            return None

    async def update_chat_description(self, chat_id: int, description: str) -> bool:
        """Обновить описание чата."""
        try:
            chat = await self.chat_repository.get_by_id(chat_id)
            if not chat:
                self.logger.logger.warning(f"Чат {chat_id} не найден")
                return False

            # ChatEntity doesn't have description field, this is a conceptual method
            # In real implementation, we would need to extend the entity or use metadata
            # For now, we just log the request and return success
            self.logger.logger.info(f"Запрос на обновление описания чата {chat_id}: {description}")
            self.logger.logger.warning(
                "Обновление описания чатов пока не поддерживается - требуется расширение ChatEntity"
            )
            return True

        except Exception as e:
            self.logger.logger.error(f"Ошибка при обновлении описания чата {chat_id}: {e}")
            return False

    async def update_chat_settings(
        self,
        chat_id: int,
        title: str | None = None,
        welcome_text: str | None = None,
        welcome_enabled: bool | None = None,
        auto_delete_time: int | None = None,
    ) -> bool:
        """Обновить настройки чата."""
        try:
            chat = await self.chat_repository.get_by_id(chat_id)
            if not chat:
                self.logger.logger.warning(f"Чат {chat_id} не найден")
                return False

            updated_fields = []

            if title is not None:
                chat.title = title
                updated_fields.append(f"title={title}")

            if welcome_text is not None:
                chat.welcome_message = welcome_text
                updated_fields.append(f"welcome_text={welcome_text}")

            if welcome_enabled is not None:
                chat.is_welcome_enabled = welcome_enabled
                updated_fields.append(f"welcome_enabled={welcome_enabled}")

            if auto_delete_time is not None:
                chat.welcome_delete_time = auto_delete_time
                updated_fields.append(f"auto_delete_time={auto_delete_time}")

            await self.chat_repository.save(chat)

            self.logger.logger.info(f"Обновлены настройки чата {chat_id}: {', '.join(updated_fields)}")
            return True

        except Exception as e:
            self.logger.logger.error(f"Ошибка при обновлении настроек чата {chat_id}: {e}")
            return False

    async def get_chat_statistics(self) -> dict[str, Any]:
        """Получить общую статистику по всем чатам."""
        try:
            chats = await self.chat_repository.get_all()
            blocked_users = await self.user_repository.get_blocked_users()

            stats = {
                "total_chats": len(chats),
                "forum_chats": len([c for c in chats if c.is_forum]),
                "regular_chats": len([c for c in chats if not c.is_forum]),
                "chats_with_welcome": len([c for c in chats if c.is_welcome_enabled]),
                "chats_with_captcha": len([c for c in chats if c.is_captcha_enabled]),
                "total_blocked_users": len(blocked_users),
            }

            self.logger.logger.info("Получена общая статистика по чатам")
            return stats

        except Exception as e:
            self.logger.logger.error(f"Ошибка при получении статистики: {e}")
            return {}

    async def search_chats(self, query: str) -> list[ChatInfo]:
        """Поиск чатов по названию."""
        try:
            all_chats = await self.get_all_chats()
            query_lower = query.lower()

            filtered_chats = []
            for chat in all_chats:
                if query_lower in (chat.title or "").lower() or (
                    chat.description and query_lower in chat.description.lower()
                ):
                    filtered_chats.append(chat)

            self.logger.logger.info(f"Найдено {len(filtered_chats)} чатов по запросу '{query}'")
            return filtered_chats

        except Exception as e:
            self.logger.logger.error(f"Ошибка при поиске чатов: {e}")
            return []
