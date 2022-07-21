import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import BoundFilter

from db.sql_aclhemy import db

# list_super_admins = [268388996, 447036451]
list_super_admins = [268388996]


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
            if chat_state == 0 and member.is_chat_admin():
                return True
            elif chat_state == 1 and (member.is_chat_admin() or admin_state):
                return True
            elif chat_state == 3 and admin_state:
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


class Memes(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        command = message.text.split()[0][1:]
        return db.check_command_state(command)


class Unmute(BoundFilter):
    async def check(self, callback: types.CallbackQuery) -> bool:
        return callback.data == 'not_bot' or callback.data == str(datetime.datetime.now().date()) and \
               db.check_verify(callback.from_user.id) is False


def setup(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(IsGroup)
    dp.filters_factory.bind(IsPrivate)
    dp.filters_factory.bind(SuperAdmins)
    dp.filters_factory.bind(Memes)
    dp.filters_factory.bind(Unmute)
