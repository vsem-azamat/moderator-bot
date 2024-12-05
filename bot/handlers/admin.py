from aiogram import types, Router
from aiogram.filters import Command

from database.repositories import AdminRepository
from bot.utils import other


router = Router()


@router.message(Command("admin", prefix="!/"))
async def new_admin(message: types.Message, admin_repo: AdminRepository):
    await admin_repo.insert_admin(message.reply_to_message.from_user.id)
    await message.answer(f"Админ {await other.get_user_mention(message.reply_to_message.from_user)} добавлен.")
    await message.delete()


@router.message(Command("unadmin", prefix="!/"))
async def delete_admin(message: types.Message, admin_repo: AdminRepository):
    await admin_repo.delete_admin(message.reply_to_message.from_user.id)
    await message.answer(f"Админ {await other.get_user_mention(message.reply_to_message.from_user)} удален.")
    await message.delete()
