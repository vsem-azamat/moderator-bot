from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import BoundFilter

from db.sql_aclhemy import db

list_super_admins = [268388996, 447036451]


class AdminFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        """
        Chats.db_admins - chat_state:
        0 - Only chat admins
        1 - Chat admins + db admins
        3 - Only db admins
        """
        member = await message.chat.get_member(message.from_user.id)
        admin_state, chat_state = db.check_chat_db_admins_state(message.from_user.id, message.chat.id)
        if message.from_user.id in list_super_admins:
            return True
        else:
            if admin_state == 0 and member.is_chat_admin():
                return True
            elif admin_state == 1 and (member.is_chat_admin() or admin_state):
                return True
            elif admin_state == 3:
                return True
            else:
                return False


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
