from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

list_super_admins = [268388996, 447036451]


class SuperAdmins(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.from_user.id in list_super_admins
