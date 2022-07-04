import re
import datetime


def mute_date_calc(message: str) -> dict:
    command_parse = re.compile(r"(!mute|/mute) ?(\d+)? ?(\b(m|h|d|w)\b)?")
    parsed = command_parse.match(message)
    time = parsed.group(2)
    unit = parsed.group(3)

    if unit is None:
        unit = 'm'

    if time is None:
        time = 5
    else:
        time = int(time)

    timedelta = {
        'm': datetime.timedelta(minutes=time),
        'h': datetime.timedelta(hours=time),
        'd': datetime.timedelta(days=time),
        'w': datetime.timedelta(weeks=time),
        None: datetime.timedelta(minutes=time)
    }.get(unit, datetime.timedelta(minutes=5))

    until_date = datetime.datetime.now() + timedelta

    return {'until_date': until_date, 'time': time, 'unit': unit}
