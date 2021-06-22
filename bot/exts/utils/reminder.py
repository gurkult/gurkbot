from datetime import datetime, timedelta

from bot.bot import Bot
from discord.ext.commands import Cog, Context, group
from loguru import logger

from bot.postgres.utils import db_execute, db_fetch

ACCEPTED_FORMATS = []


class Reminder(Cog):
    """Reminder for events, tasks, etc."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.reminders = None

        self.bot.loop.create_task(self.schedule_all_reminders())

    async def schedule_all_reminders(self):
        """Pull and schedule all reminders from the database."""
        self.reminders = (
            await db_fetch(self.bot.db_pool, "SELECT * FROM reminders WHERE is_sent=$1", False)
        )
        self.reminders = [dict(reminder) for reminder in self.reminders]
        logger.info(self.reminders)

    @staticmethod
    async def parse_duration(duration: str) -> datetime:
        """Parse duration string to datetime."""
        return datetime.now().replace(microsecond=0) + timedelta(hours=2)

    @staticmethod
    async def parse_timestamp(timestamp: str) -> datetime:
        """Parse timestamp string to datetime."""
        return datetime.now().replace(microsecond=0) + timedelta(hours=2)

    @group(name="remind", invoke_without_command=True)
    async def remind_group(self, ctx: Context, duration: str, *, content: str) -> None:
        """Set reminders."""
        await self.remind_duration(ctx, duration, content=content)

    async def schedule_reminder(self, timestamp: datetime, ctx: Context, content: str) -> None:
        """Add reminder to database and schedule it."""
        sql = "INSERT INTO reminders VALUES ($1, $2, $3, $4)"
        await db_execute(self.bot.db_pool, sql, ctx.message.id, ctx.author.id, content, timestamp)

    @remind_group.command(name="duration")
    async def remind_duration(
        self, ctx: Context, duration: str, *, content: str
    ) -> None:
        """Set reminder base on duration."""
        future_timestamp = await self.parse_duration(duration)
        await self.schedule_reminder(future_timestamp, ctx, content)

    @remind_group.command(name="timestamp")
    async def remind_timestamp(
        self, ctx: Context, timestamp: str, *, content: str
    ) -> None:
        """Set reminder base on timestamp."""
        future_timestamp = await self.parse_timestamp(timestamp)
        await self.schedule_reminder(future_timestamp, ctx, content)

    @remind_group.command(name="list")
    async def list_reminders(self, ctx: Context):
        """List all your reminders."""
        reminders = [
            reminder for reminder in self.reminders if reminder["user_id"] == ctx.author.id and not reminder["is_sent"]
        ]
        for reminder in reminders:
            await ctx.send(f"{reminder['end_time']}-{reminder['content']}")


def setup(bot: Bot) -> None:
    """Init cog."""
    bot.add_cog(Reminder(bot))
