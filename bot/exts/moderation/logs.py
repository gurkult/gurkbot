from bot.bot import Bot
from discord.ext.commands import Cog


class ModerationLog(Cog):
    """Cog used to log important actions in the community to a log channel."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot


def setup(bot: Bot) -> None:
    """Load the moderation log during setup."""
    bot.add_cog(ModerationLog(bot))
