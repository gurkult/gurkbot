from bot.bot import Bot
from discord.ext.commands import Cog


class Utils(Cog):
    """A general collection of utilities."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot


def setup(bot: Bot) -> None:
    """Setup Utils cog."""
    bot.add_cog(Utils(bot))
