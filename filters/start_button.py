from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from keyboards.default.start_menu import bt11, bt12, bt21, bt22, bt32

start_button = [bt11, bt12, bt21, bt22, bt32]


class Start_button(BoundFilter):  # filter for paging univ/less
    async def check(self, message: types.Message) -> bool:
        return message.text in start_button
