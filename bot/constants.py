import pathlib
import os

# env vars
PREFIX = os.getenv("PREFIX") or "!"
TOKEN = os.getenv("TOKEN")

# paths
EXTENIONS = pathlib.Path("bot/exts/")
