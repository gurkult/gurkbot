import pathlib
import os

# env vars
PREFIX = os.getenv("PREFIX") or "!"
TOKEN = os.getenv("TOKEN")
ANNOUNCEMENTS_ID = os.getenv("ANNOUNCEMENTS_ID", "789978290844598272")
POLLS_ID = os.getenv("POLLS_ID", "790043110360350740")

# paths
EXTENSIONS = pathlib.Path("bot/exts/")
LOG_FILE = pathlib.Path("log/gurkbot.log")
