from aiogram import types, Router
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from database import crud
from bot.utils import other
from bot.utils.filters import ChatTypeFilter, SuperAdminFilter


router = Router()


@router.message(ChatTypeFilter(['group', 'supergroup']), Command('admin', prefix='!/'), SuperAdminFilter())
async def new_admin(message: types.Message, db: AsyncSession):
    await crud.insert_admin(db, message.reply_to_message.from_user.id)
    await message.answer(f"Админ {await other.get_mention(message.reply_to_message.from_user)} добавлен.")
    await message.delete()
