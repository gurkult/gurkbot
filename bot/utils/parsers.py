import re
from datetime import datetime, timedelta
from typing import Optional

from disnake.ext.commands import BadArgument


DURATION_REGEX = re.compile(
    r"^((?P<days>[0-9]+)(d|day|days))?"
    r"((?P<hours>[0-9]+)(h|hour|hours))?"
    r"((?P<minutes>[0-9]+)(m|min|mins|minute|minutes))?"
    r"((?P<seconds>[0-9]+)(s|sec|secs|second|seconds))?$"
)


def parse_duration(duration_pattern: str) -> Optional[datetime]:
    """Parse duration string to future datetime object."""
    result = DURATION_REGEX.match(duration_pattern)
    if not result:
        return
    group_dict = {k: int(v) for k, v in result.groupdict(default="0").items()}
    try:
        return datetime.utcnow() + timedelta(**group_dict)
    except OverflowError:
        raise BadArgument("Oops! We can not take in such huge numbers...")
