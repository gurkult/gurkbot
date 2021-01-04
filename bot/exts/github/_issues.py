from typing import Union

import discord
from aiohttp import ClientSession
from bot.constants import Emojis
from discord import Embed
from discord.ext import commands
from loguru import logger


BAD_RESPONSE = {
    404: "Issue/pull request not located! Please enter a valid number!",
    403: "Rate limit has been hit! Please try again later!",
}
MAX_REQUESTS = 5
REPO_CHANNEL_MAP = {
    "793864456249278486": "reagurk",
    "793864456249278487": "gurkbot",
    "793864456249278488": "py-gurklang",
    "793864456249278489": "branding",
}


class Issues:
    """Cog that allows users to retrieve issues from GitHub."""

    def __init__(self, http_session: ClientSession) -> None:
        self.http_session = http_session

    @staticmethod
    def get_repo(channel: discord.TextChannel) -> str:
        """Get repository for the particular channel."""
        if str(channel) in REPO_CHANNEL_MAP.keys():
            return REPO_CHANNEL_MAP[str(channel)]
        else:
            return ""

    async def issue(
        self,
        channel: discord.TextChannel,
        numbers: commands.Greedy[int],
        repository: str,
        user: str,
    ) -> Union[None, Embed, str]:
        """Command to retrieve issue(s) from a GitHub repository."""
        links = []
        numbers = set(numbers)

        repo_got_for_channel = self.get_repo(channel)
        repository = repository if repository else repo_got_for_channel

        if len(numbers) > MAX_REQUESTS:
            embed = discord.Embed(
                title="Errror!",
                color=discord.Color.red(),
                description=f"Too many issues/PRs! (maximum of {MAX_REQUESTS})",
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
                return f"#{number} {BAD_RESPONSE.get(r.status)}"

            if "issues" in json_data.get("html_url"):
                icon_url = (
                    Emojis.issue
                    if json_data.get("state") == "open"
                    else Emojis.issue_closed
                )

            else:
                logger.info(
                    f"PR provided, querying GH pulls API for additional information: {merge_url}"
                )
                async with self.http_session.get(merge_url) as m:
                    if json_data.get("state") == "open":
                        icon_url = Emojis.pull_request
                    elif m.status == 204:
                        icon_url = Emojis.merge
                    else:
                        icon_url = Emojis.pull_request_closed

            issue_url = json_data.get("html_url")
            links.append(
                [
                    icon_url,
                    f"[{repository}] #{number} {json_data.get('title')}",
                    issue_url,
                ]
            )

        resp = discord.Embed(
            colour=discord.Color.green(),
            description="\n".join(["{0} [{1}]({2})".format(*link) for link in links]),
        )
        resp.set_author(name="GitHub", url=f"https://github.com/{user}/{repository}")
        return resp
