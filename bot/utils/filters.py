from aiogram import types
from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession

from config import cnfg
from database.repositories import get_admin_repository


class SuperAdminFilter(BaseFilter):
    async def __call__(self, msg: types.Message) -> bool:
        return msg.from_user.id in cnfg.SUPER_ADMINS


class AdminFilter(BaseFilter):
    async def __call__(self, msg: types.Message, db: AsyncSession) -> bool:
        admin_repo = get_admin_repository(db)
        admins_id = [admin.id for admin in await admin_repo.get_db_admins()]
        return msg.from_user.id in admins_id


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: str | list[str]):
        self.chat_type = chat_type

    async def __call__(self, message: types.Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
