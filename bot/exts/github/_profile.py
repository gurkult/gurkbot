from datetime import datetime
from typing import Optional

import discord
from aiohttp import ClientSession
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
    def get_data(username: Optional[str], user_data: dict, org_data: dict) -> dict:
        """Return filtered github data for user."""
        filtered_user_data = {}
        orgs = [org["login"] for org in org_data]

        if user_data.get("message") != "Not Found":
            # Forming blog link
            if user_data["blog"].startswith("http"):  # Blog link is complete
                blog = user_data["blog"]
            elif user_data["blog"]:  # Blog exists but the link is not complete
                blog = f"https://{user_data['blog']}"
            else:
                blog = "No website link available"

            filtered_user_data["login"] = user_data["login"]
            filtered_user_data["avatar"] = user_data["avatar_url"]
            filtered_user_data["bio"] = (
                f"```{user_data['bio']}```\n" if user_data["bio"] is not None else ""
            )
            filtered_user_data["created_at"] = user_data["created_at"]
            filtered_user_data[
                "Followers"
            ] = f"[{user_data['followers']}]({user_data['html_url']}?tab=followers)"
            filtered_user_data[
                "Following"
            ] = f"[{user_data['following']}]({user_data['html_url']}?tab=following)"
            filtered_user_data["Public repos"] = (
                f"[{user_data['public_repos']}]({user_data['html_url']}?tab"
                f"=repositories) "
            )
            filtered_user_data[
                "Gists"
            ] = f"[{user_data['public_gists']}](https://gist.github.com/{username})"
            filtered_user_data["Organizations"] = (
                " | ".join(orgs) if orgs else "No Organizations"
            )
            filtered_user_data["Website"] = blog

            return filtered_user_data

    @staticmethod
    def generate_embed(user_data: dict) -> discord.Embed:
        """Generate Embed for github profile."""
        embed = discord.Embed(
            title=f"{user_data['login']}'s GitHub profile info",
            description=user_data["bio"],
            colour=discord.Colour.green(),
            timestamp=datetime.strptime(user_data["created_at"], "%Y-%m-%dT%H:%M:%SZ"),
        )
        embed.set_thumbnail(url=user_data["avatar"])
        embed.set_footer(text="Account created at")

        embed.add_field(name="Followers", value=user_data["Followers"])
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="Following", value=user_data["Following"])
        embed.add_field(name="Public repos", value=user_data["Public repos"])
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="Gists", value=user_data["Gists"])
        embed.add_field(name="Organizations", value=user_data["Organizations"])
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="Website", value=user_data["Website"])

        return embed

    async def get_github_info(self, username: str) -> Embed:
        """Fetches a user's GitHub information."""
        user_data = await self.fetch_data(f"https://api.github.com/users/{username}")

        # User_data will not have a message key if the user exists
        if user_data.get("message") is not None:
            embed = discord.Embed(
                title="I'm sorry Gurk, I'm afraid I can't do that.",
                description=f"The profile for `{username}` was not found.",
                colour=discord.Colour.red(),
            )
            return embed

        org_data = await self.fetch_data(user_data["organizations_url"])
        user_data = self.get_data(username, user_data, org_data)

        embed = self.generate_embed(user_data)
        return embed
