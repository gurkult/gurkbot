import random

import disnake
from disnake.ext import commands
from disnake.ext.commands import Context

from bot.bot import Bot
from bot.constants import BALL_REPLIES, Colours


class EightBall(commands.Cog):
    """Cog for asking a question to the  8ball."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command(
        name="8ball",
        description="Ask any question to the bot.",
    )
    async def eight_ball(self, ctx: Context, *, question: str) -> None:
        """Sends an embed with an answer to the user's question."""
        embed = disnake.Embed(
            title="**My Answer:**",
            description=random.choice(BALL_REPLIES),
            color=Colours.green,
        )
        embed.set_footer(text=f"You asked: {question}")
        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the Eightball cog."""
    bot.add_cog(EightBall(bot))
