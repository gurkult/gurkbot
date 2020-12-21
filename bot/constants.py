import pathlib
import os

# env vars
PREFIX = os.getenv("PREFIX") or "!"
TOKEN = os.getenv("TOKEN")

# paths
EXTENSIONS = pathlib.Path("bot/exts/")
LOG_FILE = pathlib.Path("log/gurkbot.log")
