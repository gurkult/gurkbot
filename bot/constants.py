import os
import pathlib
from typing import NamedTuple

import yaml

# env vars
PREFIX = os.getenv("PREFIX") or "!"
TOKEN = os.getenv("TOKEN")
BOT_REPO_URL = "https://github.com/gurkult/gurkbot"

# paths
LOG_FILE = pathlib.Path("log/gurkbot.log")

# checking if the token is in the env file
if not TOKEN:
    raise EnvironmentError(
        "token value is None. Make sure you have configured the TOKEN field in .env"
    )


class Emojis(NamedTuple):
    issue_emoji = "<:IssueOpen:794834041450266624>"
    issue_closed_emoji = "<:IssueClosed:794834041240289321>"
    pull_request_emoji = "<:PROpen:794834041416187935>"
    pull_request_closed_emoji = "<:PRClosed:794834041073172501>"
    merge_emoji = "<:PRMerged:794834041173704744>"
    online = "<:status_online:804965842163990558>"
    offline = "<:status_offline:804965801618702367>"


class Colours:
    green = 0x1F8B4C
    yellow = 0xF1C502
    soft_red = 0xCD6D6D


class Channels(NamedTuple):
    devalerts = int(os.getenv("CHANNEL_DEVALERTS", 796695123177766982))
    devlog = int(os.getenv("CHANNEL_DEVLOG", 789431367167377448))

    dev_gurkbot = int(os.getenv("CHANNEL_DEV_GURKBOT", 789295038315495455))
    dev_reagurk = int(os.getenv("CHANNEL_DEV_REAGURK", 789241204696416287))
    dev_gurklang = int(os.getenv("CHANNEL_DEV_GURKLANG", 789249499800535071))
    dev_branding = int(os.getenv("CHANNEL_DEV_BRANDING", 789193817051234306))

class Roles(NamedTuple):
    supereme_cucmber = int(os.getenv('SUPREME_CUCUMBER'))
    steering_council = int(os.getenv('STEERING_COUNCIL'))
    lords = int(os.getenv('LORDS'))

# Bot replies
with pathlib.Path("bot/resources/bot_replies.yml").open(encoding="utf8") as file:
    bot_replies = yaml.safe_load(file)
    ERROR_REPLIES = bot_replies["ERROR_REPLIES"]
    POSITIVE_REPLIES = bot_replies["POSITIVE_REPLIES"]
    NEGATIVE_REPLIES = bot_replies["NEGATIVE_REPLIES"]
