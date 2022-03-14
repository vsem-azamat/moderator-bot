from aiogram import Dispatcher


from .admins import AdminFilter, SuperAdmins
from .chats import IsPrivate, IsGroup


def setup(dp: Dispatcher):
    pass
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(IsGroup)
    dp.filters_factory.bind(IsPrivate)
    dp.filters_factory.bind(SuperAdmins)
