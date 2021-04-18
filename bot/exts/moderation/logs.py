import textwrap
from datetime import datetime
from typing import Optional

from bot.bot import Bot
from bot.constants import Channels, Colours
from discord import Embed, TextChannel, User
from discord.ext.commands import Cog
from loguru import logger


class ModerationLog(Cog):
    """Cog used to log important actions in the community to a log channel."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.log_channel: Optional[TextChannel] = None
        super().__init__()

    async def post_message(
        self,
        actor: User,
        action: str,
        body: Optional[str] = None,
        link: Optional[str] = None,
        color: int = Colours.green,
    ) -> None:
        """Format and post a message to the #log channel."""
        logger.trace(f'Creating log "{actor.id} {action}"')

        if not self.log_channel:
            await self.bot.wait_until_ready()
            self.log_channel = await self.bot.fetch_channel(Channels.log)

            if not self.log_channel:
                logger.error(f"Failed to get the #log channel with ID {Channels.log}.")
                return

        await self.log_channel.send(
            embed=Embed(
                title=(
                    f"{actor.name}#{actor.discriminator} "
                    f"{f'({actor.display_name}) ' if actor.display_name != actor.name else ''}"
                    f"({actor.id}) {action}"
                ),
                description=textwrap.shorten(body, 2048)
                if body
                else "<no additional information provided>",
                url=link,
                color=color,
                timestamp=datetime.utcnow(),
            ).set_thumbnail(url=actor.avatar_url)
        )

    @Cog.listener()
    async def on_ready(self) -> None:
        """Post a message to #logs saying that the bot logged in."""
        await self.post_message(self.bot.user, "logged in!")


def setup(bot: Bot) -> None:
    """Load the moderation log during setup."""
    bot.add_cog(ModerationLog(bot))
