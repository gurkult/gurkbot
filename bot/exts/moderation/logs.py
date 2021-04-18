from datetime import datetime
from typing import Optional

from bot.bot import Bot
from bot.constants import Channels, Colours
from discord import Embed, Member, Message, RawMessageDeleteEvent, TextChannel, User
from discord.ext.commands import Cog
from loguru import logger


class ModerationLog(Cog):
    """Cog used to log important actions in the community to a log channel."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.log_channel: Optional[TextChannel] = None
        self.dm_log_channel: Optional[TextChannel] = None
        super().__init__()

    async def post_message(self, embed: Embed) -> Optional[Message]:
        """Send an embed to the #logs channel."""
        if not self.log_channel:
            await self.bot.wait_until_ready()
            self.log_channel = await self.bot.fetch_channel(Channels.log)

            if not self.log_channel:
                logger.error(f"Failed to get the #log channel with ID {Channels.log}.")
                return

        return await self.log_channel.send(embed=embed)

    async def post_formatted_message(
        self,
        actor: User,
        action: str,
        *,
        body: Optional[str] = None,
        link: Optional[str] = None,
        colour: int = Colours.green,
    ) -> None:
        """Format and post a message to the #log channel."""
        logger.trace(f'Creating log "{actor.id} {action}"')

        await self.post_message(
            Embed(
                title=(
                    f"{actor} "
                    f"{f'({actor.display_name}) ' if actor.display_name != actor.name else ''}"
                    f"({actor.id}) {action}"
                ),
                description=body or "<no additional information provided>",
                url=link,
                colour=colour,
                timestamp=datetime.utcnow(),
            ).set_thumbnail(url=actor.avatar_url)
        )

    @Cog.listener()
    async def on_ready(self) -> None:
        """Post a message to #logs saying that the bot logged in."""
        await self.post_formatted_message(self.bot.user, "logged in!")

    @Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent) -> None:
        """Log message deletion."""
        if message := payload.cached_message:
            if message.author.bot:
                return

            await self.post_formatted_message(
                message.author,
                f"deleted a message in #{message.channel}.",
                body=message.content,
                colour=Colours.soft_red,
            )
        else:
            await self.post_message(
                Embed(
                    title=(
                        f"Message {payload.message_id} deleted in "
                        f"#{await self.bot.fetch_channel(payload.channel_id)}."
                    ),
                    description="The message wasn't cached so it cannot be displayed.",
                    colour=Colours.soft_red,
                )
            )

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message) -> None:
        """Log message edits."""
        if after.author.bot or before.content == after.content:
            return

        await self.post_formatted_message(
            after.author,
            f"edited a message in #{after.channel}.",
            body=f"**Before:**\n{before.content}\n\n**After:**\n{after.content}",
            colour=Colours.yellow,
        )

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        """Log members joining."""
        await self.post_formatted_message(member, "joined.")

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        """Log members leaving."""
        await self.post_formatted_message(member, "left.", colour=Colours.soft_red)

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        """Log nickname changes."""
        if before.nick == after.nick:
            return

        await self.post_formatted_message(
            after, "updated their nickname.", body=f"`{before.nick}` -> `{after.nick}`"
        )

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """Log DM messages to #dm-logs."""
        # If the guild attribute is set it isn't a DM
        if message.guild:
            return

        if not self.dm_log_channel:
            await self.bot.wait_until_ready()
            self.dm_log_channel = await self.bot.fetch_channel(Channels.dm_log)

            if not self.dm_log_channel:
                logger.error(
                    f"Failed to get the #log channel with ID {Channels.dm_log}."
                )
                return

        await self.dm_log_channel.send(
            embed=Embed(
                title=f"Direct message from {message.author}",
                description=message.content,
                colour=Colours.green,
            ).set_thumbnail(url=message.author.avatar_url)
        )


def setup(bot: Bot) -> None:
    """Load the moderation log during setup."""
    bot.add_cog(ModerationLog(bot))
