from abc import ABC

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import BoundFilter

list_super_admins = [268388996, 447036451]


class AdminFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_admin() or message.from_user.id in list_super_admins


class SuperAdmins(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.from_user.id in list_super_admins


class IsPrivate(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type in (
            types.ChatType.PRIVATE
        )


class IsGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type in (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP
        )


def setup(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(IsGroup)
    dp.filters_factory.bind(IsPrivate)
    dp.filters_factory.bind(SuperAdmins)
