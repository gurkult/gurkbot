import discord
from discord.ext import commands
from discord.ext.commands import Bot
from bot.constants import MC_SERVER_ADDRESS, Colours

from mcstatus import MinecraftServer


class Minecraft(commands.Cog):
    """Minecraft Cog"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.server = MinecraftServer.lookup(MC_SERVER_ADDRESS)

    @commands.command()
    async def mcstatus(self, ctx: commands.Context) -> None:
        """Collects data from minecraft server"""
        status = self.server.status()
        players = [user["name"] for user in status.raw["players"]["sample"]]
        embed = discord.Embed(
            title="Gurkcraft", description=embed_value, color=Colours.green
        )
        embed.add_field(name="Server", value="mc.gurkult.com")
        embed.add_field(name="Server Latency", value=f"{status.latency}ms")
        embed.add_field(name="Gurkans Online", value=status.players.online)
        embed.add_field(name="Gurkans Connected", value=", ".join(players))
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    """Loading the Minecraft cog."""
    bot.add_cog(Minecraft(bot))
