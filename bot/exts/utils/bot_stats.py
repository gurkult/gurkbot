from datetime import datetime
from platform import python_version

import humanize

from bot.bot import Bot
from bot.constants import Colours
from discord import Embed, __version__
from discord.ext import commands


class BotStats(commands.Cog):
    """Get info about the bot."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Ping the bot to see its latency."""
        embed = Embed(
            title="Pong!",
            description=f"Gateway Latency: {round(self.bot.latency * 1000)}ms",
            color=Colours.green,
        )
        await ctx.send(content=ctx.author.mention, embed=embed)

    @commands.command()
    async def stats(self, ctx: commands.Context) -> None:
        """Get the information and current uptime of the bot."""
        embed = Embed(
            title="Bot Stats",
            color=Colours.green,
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)

        uptime = humanize.precisedelta(datetime.utcnow().timestamp() - self.bot.launch_time)

        fields = [
            ("Python Version", python_version()),
            ("discord.py Version", __version__),
            ("Uptime", uptime),
        ]

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)
        await ctx.send(content=ctx.author.mention, embed=embed)


def setup(bot: Bot) -> None:
    """Loads the botstats cog."""
    bot.add_cog(BotStats(bot))
