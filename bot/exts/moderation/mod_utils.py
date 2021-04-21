from bot.bot import Bot
from bot.constants import Roles
from discord import Forbidden, Member
from discord.ext.commands import Cog, Context, command, has_any_role
from loguru import logger


class ModUtils(Cog):
    """Cog used for various moderation utility commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        super().__init__()

    @command(aliases=("dm",))
    @has_any_role(Roles.moderators, Roles.steering_council)
    async def send_dm(self, ctx: Context, user: Member, *, message: str) -> None:
        """Send a DM to the specified user."""
        logger.info(f"Sending message {message!r} to {user}.")
        try:
            await user.send(message)
        except Forbidden:
            await ctx.message.add_reaction("\N{CROSS MARK}")
        else:
            await ctx.message.add_reaction("\N{OK HAND SIGN}")


def setup(bot: Bot) -> None:
    """Load the moderation utils cog during setup."""
    bot.add_cog(ModUtils(bot))
