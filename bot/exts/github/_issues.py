from random import choice
from typing import Optional

import disnake
from aiohttp import ClientSession
from bot.constants import Channels, ERROR_REPLIES, Emojis
from disnake import Embed
from disnake.ext import commands
from loguru import logger

BAD_RESPONSE = {
    404: "Issue/pull request not located! Please enter a valid number!",
    403: "Rate limit has been hit! Please try again later!",
}
MAX_REQUESTS = 5
REPO_CHANNEL_MAP = {
    Channels.dev_reagurk: "reagurk",
    Channels.dev_gurkbot: "gurkbot",
    Channels.dev_gurklang: "py-gurklang",
    Channels.dev_branding: "branding",
}


class Issues:
    """Cog that allows users to retrieve issues from GitHub."""

    def __init__(self, http_session: ClientSession) -> None:
        self.http_session = http_session

    @staticmethod
    def get_repo(channel: disnake.TextChannel) -> Optional[str]:
        """Get repository for the particular channel."""
        return REPO_CHANNEL_MAP.get(channel.id, "gurkbot")

    @staticmethod
    def error_embed(error_msg: str) -> Embed:
        """Generate Error Embed for Issues command."""
        embed = disnake.Embed(
            title=choice(ERROR_REPLIES),
            color=disnake.Color.red(),
            description=error_msg,
        )
        return embed

    async def issue(
        self,
        channel: disnake.TextChannel,
        numbers: commands.Greedy[int],
        repository: Optional[str],
        user: str,
    ) -> Embed:
        """Retrieve issue(s) from a GitHub repository."""
        links = []
        numbers = set(numbers)

        repository = repository if repository else self.get_repo(channel)

        if len(numbers) > MAX_REQUESTS:
            embed = self.error_embed(
                "You can specify a maximum of {MAX_REQUESTS} issues/PRs only."
            )
            return embed

        for number in numbers:
            url = f"https://api.github.com/repos/{user}/{repository}/issues/{number}"
            merge_url = (
                f"https://api.github.com/repos/{user}/{repository}/pulls/{number}/merge"
            )

            logger.trace(f"Querying GH issues API: {url}")
            async with self.http_session.get(url) as r:
                json_data = await r.json()

            if r.status in BAD_RESPONSE:
                logger.warning(f"Received response {r.status} from: {url}")
                embed = self.error_embed(f"#{number} {BAD_RESPONSE.get(r.status)}")
                return embed

            if "issues" in json_data.get("html_url"):
                icon_url = (
                    Emojis.issue_emoji
                    if json_data.get("state") == "open"
                    else Emojis.issue_closed_emoji
                )

            else:
                logger.info(
                    f"PR provided, querying GH pulls API for additional information: {merge_url}"
                )
                async with self.http_session.get(merge_url) as m:
                    if json_data.get("state") == "open":
                        icon_url = Emojis.pull_request_emoji
                    elif m.status == 204:
                        icon_url = Emojis.merge_emoji
                    else:
                        icon_url = Emojis.pull_request_closed_emoji

            issue_url = json_data.get("html_url")
            links.append(
                (
                    icon_url,
                    f"[{user}/{repository}] #{number} {json_data.get('title')}",
                    issue_url,
                )
            )

        resp = disnake.Embed(
            colour=disnake.Color.green(),
            description="\n".join("{0} [{1}]({2})".format(*link) for link in links),
        )
        resp.set_author(name="GitHub", url=f"https://github.com/{user}/{repository}")
        return resp
