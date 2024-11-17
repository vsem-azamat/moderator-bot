import re
import asyncio
import datetime
from pytz import timezone
from aiogram import types


async def sleep_and_delete(message: types.Message, seconds: int = 60):
    await asyncio.sleep(seconds)
    await message.delete()


async def get_mention(user: types.User) -> str:
    return user.mention_html()


class MuteDuration:
    def __init__(self, until_date: datetime.datetime, time: int, unit: str):
        self.until_date = until_date
        self.time = time
        self.unit = unit

    def formatted_until_date(self):
        return self.until_date.strftime("%Y-%m-%d %H:%M:%S")


def calculate_mute_duration(message: str) -> MuteDuration:
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
