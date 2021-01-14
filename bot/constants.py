import os
import pathlib

from collections import namedtuple
from enum import Enum
from typing import NamedTuple

import yaml
from loguru import logger


if os.path.exists(f'bot/config/config.yaml'):
    logger.inof(f'Found config.yaml file, setting the constants from there.')
    with open('bot/config/config.yaml') as f:
        config = yaml.safe_load(f)
else:
    logger.info('Could not find config.yaml, loading the constants from default config.')
    with open('bot/config/default-confi.yaml') as f:
        config = yaml.safe_load(f)


class Colour(Enum):
    green = 0x1F8B4C
    yellow = 0xF1C502
    soft_red = 0xCD6D6D


class Gurkbot:
    prefix = config['Bot']['Prefix']
    repo_url = "https://github.com/gurkult/gurkbot"
    token = os.getenv('TOKEN')


Channels = namedtuple(
    'Channels',
    [channel.lower() for channel in config['Channels'].keys()],
    defaults=iter(config['Channels'].values()),
)


Roles = namedtuple(
    'Roles',
    [role.lower() for role in config['Roles'].keys()],
    defaults=iter(config['Roles'].values()),
)

ERROR_REPLIES = [
    "Please don't do that.",
    "You have to stop.",
    "Do you mind?",
    "In the future, don't do that.",
    "That was a mistake.",
    "You blew it.",
    "You're bad at computers.",
    "Are you trying to kill me?",
    "Noooooo!!",
    "I can't believe you've done this"
]

NEGATIVE_REPLIES = [
    "Noooooo!!",
    "Nope.",
    "I'm sorry Gurk, I'm afraid I can't do that.",
    "I don't think so., Not gonna happen.",
    "Out of the question.",
    "Huh? No.",
    "Nah.",
    "Naw.",
    "Not likely.",
    "Not in a million years.",
    "Fat chance.",
    "Certainly not.",
    "NEGATORY.",
    "Nuh-uh.",
    "Not in my house!"
]

POSITIVE_REPLIES = [
    "Yep., Absolutely!",
    "Can do!",
    "Affirmative!",
    "Yeah okay.",
    "Sure.",
    "Sure thing!",
    "You're the boss!",
    "Okay.",
    "No problem.",
    "I got you.",
    "Alright.",
    "You got it!",
    "ROGER THAT",
    "Of course!",
    "Aye aye, cap'n!",
    "I'll allow it."
]

# paths
EXTENSIONS = pathlib.Path("bot/exts/")
LOG_FILE = pathlib.Path("log/gurkbot.log")
