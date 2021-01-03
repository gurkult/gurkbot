import pathlib
import os
from typing import NamedTuple

# env vars
PREFIX = os.getenv("PREFIX") or "!"
TOKEN = os.getenv("TOKEN")

# paths
EXTENSIONS = pathlib.Path("bot/exts/")
LOG_FILE = pathlib.Path("log/gurkbot.log")


class Emojis(NamedTuple):
    issue = "<:IssueOpen:794119024367632405>"
    issue_closed = "<:IssueClosed:794118652219359253>"
    pull_request = "<:PROpen:794118652014231562>"
    pull_request_closed = "<:PRClosed:794120818908463134>"
    merge = "<:PRMerged:794119023687761941>"
