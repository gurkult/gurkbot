from datetime import datetime

from bot.bot import Bot
from discord.ext.commands import Cog, Context, group

ACCEPTED_FORMATS = []


class Reminder(Cog):
    """Reminder for events, tasks, etc."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    async def parse_duration(duration: str) -> datetime:
        """Parse duration string to datetime."""
        ...

    @staticmethod
    async def parse_timestamp(timestamp: str) -> datetime:
        """Parse timestamp string to datetime."""
        ...

    @group(name="remind")
    async def remind_group(self, ctx: Context, duration: str, *, message: str) -> None:
        """Set reminders."""
        await self.remind_duration(ctx, duration, message)

    @remind_group.command(name="duration")
    async def remind_duration(
        self, ctx: Context, duration: str, *, message: str
    ) -> None:
        """Set reminder base on duration."""
        duration = self.parse_duration(duration)

    @remind_group.command(name="timestamp")
    async def remind_timestamp(
        self, ctx: Context, timestamp: str, *, message: str
    ) -> None:
        """Set reminder base on timestamp."""
        timestamp = self.parse_timestamp(timestamp)


def setup(bot: Bot) -> None:
    """Init cog."""
    bot.add_cog(Reminder(bot))
