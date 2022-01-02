from typing import Callable, Optional

from bot.bot import Bot
from bot.constants import Colours, Roles
from bot.exts.moderation.logs import get_post_formatted_message
from disnake import Forbidden, Member
from disnake.ext.commands import Cog, Context, command, has_any_role
from loguru import logger


class ModUtils(Cog):
    """Cog used for various moderation utility commands."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.post_formatted_message: Optional[Callable] = None
        super().__init__()

    @command(aliases=("dm",))
    @has_any_role(Roles.moderators, Roles.steering_council)
    async def send_dm(self, ctx: Context, user: Member, *, message: str) -> None:
        """Send a DM to the specified user."""
        logger.info(f"Sending message {message!r} to {user}.")

        if not self.post_formatted_message:
            self.post_formatted_message = get_post_formatted_message(self.bot)

        try:
            await user.send(message)
        except Forbidden:
            await ctx.message.add_reaction("\N{CROSS MARK}")
            await self.post_formatted_message(
                ctx.author,
                f"tried to send a message to {user.id} but it failed.",
                body=message,
                colour=Colours.soft_red,
            )
        else:
            await ctx.message.add_reaction("\N{OK HAND SIGN}")
            await self.post_formatted_message(
                ctx.author, f"sent a message to {user.id}.", body=message
            )


def setup(bot: Bot) -> None:
    """Load the moderation utils cog during setup."""
    bot.add_cog(ModUtils(bot))
