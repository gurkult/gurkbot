"""
Useful utilities for timestamps and discord times.

MIT License

Copyright (c) 2021 discord-modmail

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import datetime
import enum


class TimeStampEnum(enum.Enum):
    """
    Timestamp modes for discord.

    Full docs on this format are viewable here:
    https://discord.com/developers/docs/reference#message-formatting
    """

    # fmt: off
    SHORT_TIME = "t"        # 16:20
    LONG_TIME = "T"         # 16:20:30
    SHORT_DATE = "d"        # 20/04/2021
    LONG_DATE = "D"         # 20 April 2021
    SHORT_DATE_TIME = "f"   # 20 April 2021 16:20
    LONG_DATE_TIME = "F"    # Tuesday, 20 April 2021 16:20
    RELATIVE_TIME = "R"     # 2 months ago

    # fmt: on
    # DEFAULT alised to the default, so for all purposes, it behaves like SHORT_DATE_TIME, including the name
    DEFAULT = SHORT_DATE_TIME


def get_timestamp(
    timestamp: datetime.datetime, format: TimeStampEnum = TimeStampEnum.DEFAULT
) -> str:
    """
    Return a discord formatted timestamp from a datetime compatiable datatype.

    `format` must be an enum member of TimeStampEnum. Default style is SHORT_DATE_TIME
    """
    return f"<t:{int(timestamp.timestamp())}:{format.value}>"
