from __future__ import annotations

import os
import typing
from functools import partial, partialmethod

import loguru
from bot.command import Command
from discord.ext import commands
from loguru import logger

from .constants import LOG_FILE


def should_rotate(message: loguru.Message, file: typing.TextIO) -> bool:
    """When should the bot rotate : Once in 1 week or if the size is greater than 5 MB."""
    filepath = os.path.abspath(file.name)
    creation = os.path.getmtime(filepath)
    now = message.record["time"].timestamp()
    max_time = 7 * 24 * 60 * 60  # 1 week in seconds
    if file.tell() + len(message) > 5 * (2 ** 20):  # if greater than size 5 MB
        return True
    if now - creation > max_time:
        return True
    return False


logger.add(LOG_FILE, rotation=should_rotate)
logger.info("Logging Process Started")


# Monkey-patch discord.py decorators to use the Command subclass which supports root aliases.
# Must be patched before any cogs are added.
commands.command = partial(commands.command, cls=Command)
commands.GroupMixin.command = partialmethod(commands.GroupMixin.command, cls=Command)
