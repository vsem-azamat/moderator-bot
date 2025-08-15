import asyncio
import datetime
import re

from aiogram import types
from pytz import timezone


async def sleep_and_delete(message: types.Message, seconds: int = 60) -> None:
    """Delete a message after a short delay."""
    await asyncio.sleep(seconds)
    await message.delete()


async def get_user_mention(user: types.User) -> str:
    """Return mention markup for a user."""
    return user.mention_html()


async def get_chat_mention(tg_object: types.Message | types.Chat) -> str:
    """Return HTML link to a chat or its message."""
    chat_link = await get_chat_link(tg_object)
    if isinstance(tg_object, types.Message):
        return f'<a href="{chat_link}">{tg_object.chat.title}</a>'
    return f'<a href="{chat_link}">{tg_object.title}</a>'


async def get_message_mention(message: types.Message) -> str:
    chat_link = await get_message_link(message)
    return f'<a href="{chat_link}">Cообщение</a>'


async def get_message_link(tg_object: types.Message | types.Chat) -> str:
    """Generate a direct link to a message."""
    chat = tg_object.chat if isinstance(tg_object, types.Message) else tg_object

    if chat.username:  # Public chat or channel
        return f"https://t.me/{chat.username}/{tg_object.message_id}"

    if chat.type in ["group", "supergroup"]:  # Private group without username
        return f"https://t.me/c/{str(chat.id)[4:]}/{tg_object.message_id}"

    # Private 1-on-1 chat
    return f"https://t.me/{chat.id}/{tg_object.message_id}"


async def get_chat_link(tg_object: types.Message | types.Chat) -> str:
    """Return a direct link to a chat."""
    chat = tg_object.chat if isinstance(tg_object, types.Message) else tg_object

    if chat.username:
        return f"https://t.me/{chat.username}"
    return f"https://t.me/c/{str(chat.id)[4:]}"


class MuteDuration:
    def __init__(self, until_date: datetime.datetime, time: int, unit: str):
        self.until_date = until_date
        self.time = time
        self.unit = unit

    def formatted_until_date(self):
        return self.until_date.strftime("%Y-%m-%d %H:%M:%S")


def calculate_mute_duration(message: str) -> MuteDuration:
    """Parse /mute command and calculate mute duration."""
    command_parse = re.compile(r"(!mute|/mute) ?(\d+)? ?(m|h|d|w)?")
    parsed = command_parse.match(message)

    time = int(parsed.group(2) or 5)
    unit = parsed.group(3) or "m"

    # Define time units and calculate the duration
    units = {
        "m": datetime.timedelta(minutes=time),
        "h": datetime.timedelta(hours=time),
        "d": datetime.timedelta(days=time),
        "w": datetime.timedelta(weeks=time),
    }
    timedelta = units.get(unit, datetime.timedelta(minutes=5))
    local_tz = timezone("Europe/Prague")
    until_date = datetime.datetime.now().astimezone(local_tz) + timedelta

    return MuteDuration(until_date, time, unit)
