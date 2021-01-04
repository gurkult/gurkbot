import pathlib
import os
import typing

# env vars
PREFIX = os.getenv("PREFIX") or "!"
TOKEN = os.getenv("TOKEN")


class Roles(typing.NamedTuple):
    announcements = int(os.getenv("ANNOUNCEMENTS_ID", "789978290844598272"))
    polls = int(os.getenv("POLLS_ID", "790043110360350740"))


class Emojis(typing.NamedTuple):
    confirmation = "<:yes:794231332770938901>"
    warning = "\u26a0"


class Colors(typing.NamedTuple):
    green = 0x32A05A


# paths
EXTENSIONS = pathlib.Path("bot/exts/")
LOG_FILE = pathlib.Path("log/gurkbot.log")
