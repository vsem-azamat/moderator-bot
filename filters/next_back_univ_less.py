from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class NextBackUL(BoundFilter):  # filter for paging univ/less
    async def check(self, callback_query: types.CallbackQuery) -> bool:
        return callback_query.data == "sort_univ" or callback_query.data == "sort_less"
