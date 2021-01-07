import pathlib
import os

# env vars
from typing import NamedTuple

PREFIX = os.getenv("PREFIX") or "!"
TOKEN = os.getenv("TOKEN")
BOT_REPO_URL = "https://github.com/gurkult/gurkbot"

# paths
EXTENSIONS = pathlib.Path("bot/exts/")
LOG_FILE = pathlib.Path("log/gurkbot.log")


class Channels(NamedTuple):
    devlog = int(os.environ.get("CHANNEL_DEVLOG", 789431367167377448))


class Emojis(NamedTuple):
    cucumber = "🥒"
    invalid = "❌"
