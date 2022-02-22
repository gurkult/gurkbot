import asyncio
import random

import disnake
from disnake.ext import commands
from disnake.ext.commands import Context

from bot.bot import Bot
from bot.constants import Colours


class CoinFlip(commands.Cog):
    """Flip a coin."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command(
        name="coinflip",
        description="Toss a coin.",
    )
    async def coin_flip(
        self,
        ctx: Context,
    ) -> None:
        """Flips a coin and sends an embed with the outcome."""
        coin_choice = ["Heads 🪙", "Tails 🪙"]
        embed = disnake.Embed(
            title="**Coin Toss Outcome:**",
            description=random.choice(coin_choice),
            color=Colours.green,
        )
        await ctx.trigger_typing()
        await asyncio.sleep(1)
        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the CoinFlip cog."""
    bot.add_cog(CoinFlip(bot))
