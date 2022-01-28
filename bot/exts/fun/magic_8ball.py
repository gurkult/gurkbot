import random

import disnake
from disnake.ext import commands
from disnake.ext.commands import Context

from bot.bot import Bot
from bot.constants import Colours


class Eightball(commands.Cog, name="eightball"):
    """Cog for asking a question to the  8ball."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command(
        name="8ball",
        description="Ask any question to the bot.",
    )
    async def eight_ball(self, ctx: Context, *, question: str) -> None:
        """Sends an embed with an answer to the user's question."""
        replies = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",
        ]
        embed = disnake.Embed(
            title="**My Answer:**",
            description=f"{random.choice(replies)}",
            color=Colours.green,
        )
        embed.set_footer(text=f"You asked: {question}")
        await context.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Load the Eightball cog."""
    bot.add_cog(Eightball(bot))
