from discord.ext import commands
from discord.utils import find
import re


class MakeGurkan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.bot:
            return
        if before.display_name != after.display_name:
            role = find(lambda r: r.name == "Gurkans", after.guild.roles)
            if re.search(r"g?urk?a?n?", str(after.display_name)):
                await after.add_roles(role)
            else:
                await after.remove_roles(role)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        role = find(lambda r: r.name == "Gurkans", member.guild.roles)
        if re.search(r"g?urk?a?n?", str(member.name)):
            await member.add_roles(role)
