from aiogram import types, Router
from aiogram.filters import Command

from app.infrastructure.db.repositories import AdminRepository
from app.presentation.telegram.utils import other


router = Router()


@router.message(Command("admin", prefix="!/"))
async def new_admin(message: types.Message, admin_repo: AdminRepository):
    target_user = message.reply_to_message.from_user
    if not await admin_repo.is_admin(target_user.id):
        await admin_repo.insert_admin(target_user.id)
        await message.answer(f"Админ {await other.get_user_mention(target_user)} добавлен.")
    else:
        await message.answer(f"Админ {await other.get_user_mention(target_user)} уже есть в базе.")
    await message.delete()


@router.message(Command("unadmin", prefix="!/"))
async def delete_admin(message: types.Message, admin_repo: AdminRepository):
    target_user = message.reply_to_message.from_user
    if await admin_repo.is_admin(target_user.id):
        await admin_repo.delete_admin(target_user.id)
        await message.answer(f"Админ {await other.get_user_mention(target_user)} удален.")
    else:
        await message.answer(f"Админ {await other.get_user_mention(target_user)} не является админом.")
    await message.delete()
