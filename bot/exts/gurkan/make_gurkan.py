import re

import discord
from bot.bot import Bot
from bot.constants import Roles
from discord.ext import commands
from discord.utils import get


class MakeGurkan(commands.Cog):
    """Make Gurkan Cog adds or removes the gurkan role depending on if the user has gurkan in their name."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        """
        Adds/Removes the role on member update.

        When the member updates their nickname or username, this function will check if member is
        classified to be a gurkan or not.
        """
        if after.bot:
            return
        if before.display_name != after.display_name:
            role = get(after.guild.roles, id=Roles.gurkans)
            if re.search(r"gurk|urkan", str(after.display_name)):
                await after.add_roles(role)
            else:
                await after.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """When the member joins, this function will check if member is classified to be a gurkan or not."""
        if member.bot:
            return
        role = get(member.guild.roles, id=Roles.gurkans)
        if re.search(r"gurk|urkan", str(member.name)):
            await member.add_roles(role)


def setup(bot: commands.Bot) -> None:
    """Load the Cog."""
    bot.add_cog(MakeGurkan(bot))
