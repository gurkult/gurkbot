from datetime import datetime
from random import choice
from typing import Optional

import discord
from aiohttp import ClientSession
from bot.constants import ERROR_REPLIES
from discord import Embed


class GithubInfo:
    """Fetches info from GitHub."""

    def __init__(self, http_session: ClientSession) -> None:
        self.http_session = http_session

    async def fetch_data(self, url: str) -> dict:
        """Retrieve data as a dictionary."""
        async with self.http_session.get(url) as r:
            return await r.json()

    @staticmethod
    def get_data(username: Optional[str], user_data: dict, org_data: dict) -> Embed:
        """Return embed containing filtered github data for user."""
        orgs = [org["login"] for org in org_data]

        if user_data.get("message") != "Not Found":
            # Forming blog link
            if user_data["blog"].startswith("http"):  # Blog link is complete
                blog = user_data["blog"]
            elif user_data["blog"]:  # Blog exists but the link is not complete
                blog = f"https://{user_data['blog']}"
            else:
                blog = "No website link available"

            embed = discord.Embed(
                title=f"{user_data['login']}'s GitHub profile info",
                description=f"```{user_data['bio']}```\n"
                if user_data["bio"] is not None
                else "",
                colour=discord.Colour.green(),
                timestamp=datetime.strptime(
                    user_data["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                ),
            )
            embed.set_thumbnail(url=user_data["avatar_url"])
            embed.set_footer(text="Account created at")

            embed.add_field(
                name="Followers",
                value=f"[{user_data['followers']}]({user_data['html_url']}?tab=followers)",
            )
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(
                name="Following",
                value=f"[{user_data['following']}]({user_data['html_url']}?tab=following)",
            )
            embed.add_field(
                name="Public repos",
                value=f"[{user_data['public_repos']}]({user_data['html_url']}?tab=repositories)",
            )
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(
                name="Gists",
                value=f"[{user_data['public_gists']}](https://gist.github.com/{username})",
            )
            embed.add_field(
                name="Organizations",
                value=" | ".join(orgs) if orgs else "No Organizations",
            )
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Website", value=blog)

            return embed

    async def get_github_info(self, username: str) -> Embed:
        """Fetches a user's GitHub information."""
        user_data = await self.fetch_data(f"https://api.github.com/users/{username}")

        # User_data will not have a message key if the user exists
        if user_data.get("message") is not None:
            embed = discord.Embed(
                title=choice(ERROR_REPLIES),
                description=f"The profile for `{username}` was not found.",
                colour=discord.Colour.red(),
            )
            return embed

        org_data = await self.fetch_data(user_data["organizations_url"])
        embed = self.get_data(username, user_data, org_data)

        return embed
