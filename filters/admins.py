from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

list_super_admins = [268388996, 447036451]


class AdminFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_admin() or message.from_user.id in list_super_admins
