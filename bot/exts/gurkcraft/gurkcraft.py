import discord
from typing import NoReturn
from discord.ext import commands
from discord.ext.commands import Bot
from bot.constants import MC_SERVER, MC_PORT, Colours

from mcstatus import MinecraftServer


class Minecraft(commands.Cog):
    """Minecraft Cog"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.server = MinecraftServer(MC_SERVER, MC_PORT)

    @commands.command()
    async def mcstatus(self, ctx: commands.Context) -> None:
        """Collects data from minecraft server"""
        status = self.server.status()
        players = [user["name"] for user in status.raw["players"]["sample"]]
        embed_value = f"""\
        Server: mc.gurkult.com
        Server Latency: {status.latency}ms
        Gurkans Online: {status.players.online}
        Gurkans Connected: {", ".join(players) if status.players.online else ""}\
        """

        embed = discord.Embed(
            title="Gurkcraft", description=embed_value, color=Colours.green
        )
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    """Loading the Minecraft cog."""
    bot.add_cog(Minecraft(bot))
