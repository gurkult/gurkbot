from datetime import datetime

import humanize
from bot.bot import Bot
from bot.utils.parsers import parse_duration
from discord import Embed
from discord.ext.commands import Cog, Context, group
from loguru import logger

from bot.postgres.utils import db_fetch


REMINDER_DESCRIPTION = (
    "**Reminder ID**: {reminder_id}\n"
    "**Arrive in**: {arrive_in}\n"
    "\n**Content**:\n{content}"
)


class Reminder(Cog):
    """Reminder for events, tasks, etc."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.reminders = None
        self.current_scheduled = None

        self.bot.loop.create_task(self.schedule_latest_reminder())

    async def schedule_latest_reminder(self):
        """Pull and schedule all reminders from the database."""
        self.reminders = (
            await db_fetch(self.bot.db_pool, "SELECT * FROM reminders WHERE sent=$1 and ", False)
        )
        self.reminders = [dict(reminder) for reminder in self.reminders]
        logger.info(self.reminders)

    @group(name="remind", invoke_without_command=True)
    async def remind_group(self, ctx: Context, duration: str, *, content: str) -> None:
        """Set reminders."""
        await self.remind_duration(ctx, duration, content=content)

    async def schedule_reminder(self, timestamp: datetime, ctx: Context, content: str) -> None:
        """Add reminder to database and schedule it."""
        sql = (
            "INSERT INTO reminders(message_id, user_id, end_time, content) VALUES ($1, $2, $3, $4)RETURNING reminder_id"
        )
        async with self.bot.db_pool.acquire() as connection:
            reminder_id = await connection.fetchval(sql, ctx.message.id, ctx.author.id, timestamp, content)

        embed = Embed()
        embed.title = "New Reminder Set."
        embed.description = REMINDER_DESCRIPTION.format(
            reminder_id=reminder_id,
            arrive_in=humanize.precisedelta(timestamp - datetime.utcnow(), minimum_unit="seconds"),
            content=content[:50]
        )
        await ctx.send(embed=embed)

    @remind_group.command(name="duration")
    async def remind_duration(
        self, ctx: Context, duration: str, *, content: str
    ) -> None:
        """Set reminder base on duration."""
        future_timestamp = parse_duration(duration)
        if not future_timestamp:
            await ctx.send("Invalid duration!")
            return
        await self.schedule_reminder(future_timestamp, ctx, content)

    # @remind_group.command(name="timestamp")
    # async def remind_timestamp(
    #     self, ctx: Context, timestamp: str, *, content: str
    # ) -> None:
    #     """Set reminder base on timestamp."""
    #     future_timestamp = await self.parse_timestamp(timestamp)
    #     await self.schedule_reminder(future_timestamp, ctx, content)

    @remind_group.command(name="list")
    async def list_reminders(self, ctx: Context):
        """List all your reminders."""
        reminders = [
            reminder for reminder in self.reminders if reminder["user_id"] == ctx.author.id and not reminder["sent"]
        ]
        for reminder in reminders:
            await ctx.send(f"{reminder['end_time']}-{reminder['content']}")


def setup(bot: Bot) -> None:
    """Init cog."""
    bot.add_cog(Reminder(bot))
