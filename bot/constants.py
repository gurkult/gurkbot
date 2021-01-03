import pathlib
import os

# env vars
PREFIX = os.getenv("PREFIX") or "!"
TOKEN = os.getenv("TOKEN")
ANNOUNCEMENTS_ID = int(os.getenv("ANNOUNCEMENTS_ID", "789978290844598272"))
POLLS_ID = int(os.getenv("POLLS_ID", "790043110360350740"))


class Emojis:
    confirmation_emoji = "<:yes:794231332770938901>"
    warning_emoji = "\u26a0"


class Colors:
    GREEN = 0x32A05A


# paths
EXTENSIONS = pathlib.Path("bot/exts/")
LOG_FILE = pathlib.Path("log/gurkbot.log")
