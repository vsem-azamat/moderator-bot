import asyncio
from aiogram import BaseMiddleware, types
from aiogram.types import TelegramObject
from typing import Callable, Awaitable, Dict, Any

from config import cnfg
from app.infrastructure.db.repositories import AdminRepository


async def you_are_not_admin(event: TelegramObject, text: str = "You are not an Admin.") -> None:
    if isinstance(event, types.Message):
        asnwer = await event.answer(text)
        event.delete()
        await asyncio.sleep(5)
        await asnwer.delete()


class SuperAdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, types.Message) and event.from_user.id in cnfg.SUPER_ADMINS:
            return await handler(event, data)
        await you_are_not_admin(event, "You are not a Super Admin.")
        return  # Stop further handler processing if not SuperAdmin


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        admin_repo: AdminRepository = data["admin_repo"]
        admins_id = [admin.id for admin in await admin_repo.get_db_admins()]
        all_admins_id = admins_id + cnfg.SUPER_ADMINS
        if isinstance(event, types.Message) and event.from_user.id in all_admins_id:
            return await handler(event, data)
        await you_are_not_admin(event)
        return  # Stop further handler processing if not Admin


class AnyAdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        admin_repo: AdminRepository = data["admin_repo"]
        admins_id = [admin.id for admin in await admin_repo.get_db_admins()]
        if isinstance(event, types.Message) and (event.from_user.id in admins_id or event.from_user.id in cnfg.SUPER_ADMINS):
            return await handler(event, data)
        await you_are_not_admin(event)
        return  # Stop further handler processing if not AnyAdmin
