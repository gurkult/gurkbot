from discord.ext import commands
from discord.utils import find
import re


class MakeGurkan(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        """When the member updates their nicknames, this function will check if member is classified to be a gurkan or not."""
        if after.bot:
            return
        if before.display_name != after.display_name:
            role = find(lambda r: r.name == "Gurkans", after.guild.roles)
            if re.search(r"g?urk?a?n?", str(after.display_name)):
                await after.add_roles(role)
            else:
                await after.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
         """When the member updates their username, this function will check if member is classified to be a gurkan or not."""
        if member.bot:
            return
        role = find(lambda r: r.name == "Gurkans", member.guild.roles)
        if re.search(r"g?urk?a?n?", str(member.name)):
            await member.add_roles(role)
