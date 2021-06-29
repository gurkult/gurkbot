import asyncio
import re
from contextlib import suppress
from datetime import datetime
from typing import Optional, Union

import discord
import humanize
from asyncpg import Record
from bot.bot import Bot
from bot.postgres.utils import db_execute
from bot.utils.pagination import LinePaginator
from bot.utils.parsers import parse_duration
from discord import Embed
from discord.utils import sleep_until
from discord.ext.commands import Cog, Context, group


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
        self.reminders: dict = {}
        self.current_scheduled: Optional[int] = None
        self.scheduled_coroutine: Optional[asyncio.Task] = None

        self.bot.loop.create_task(self._sync_reminders())

    def get_recent_reminder(self) -> Optional[dict]:
        with suppress(ValueError):
            return min(self.reminders.values(), key=lambda record: record["end_time"])
        return

    async def _sync_reminders(self):
        self.reminders = {
            reminder["reminder_id"]: reminder
            for reminder in await db_fetch(self.bot.db_pool, "SELECT * FROM reminders")
        }
        await self.schedule_reminder(self.get_recent_reminder())

    async def cancel_reminder_task(self) -> None:
        """Cancel reminder task."""
        if isinstance(self.scheduled_coroutine, asyncio.Task):
            self.scheduled_coroutine.cancel()

        self.scheduled_coroutine = None

    async def schedule_reminder(self, recent: Optional[dict]) -> None:
        """Pull and schedule all reminders from the database."""
        if not recent:
            self.current_scheduled = None
            return

        if recent["reminder_id"] != self.current_scheduled:
            self.current_scheduled = recent["reminder_id"]

            # Cancel old reminder for more recent reminder.
            await self.cancel_reminder_task()

            self.scheduled_coroutine = self.bot.loop.create_task(self.send_reminder(recent))

    async def send_reminder(self, reminder: Union[Record, dict]) -> None:
        """Send scheduled reminder."""
        if (until := reminder["end_time"]) > datetime.utcnow():
            await sleep_until(until)

        await self.bot.wait_until_ready()
        user: discord.User = self.bot.get_user(reminder["user_id"])
        channel: discord.TextChannel = self.bot.get_channel(reminder["channel_id"])

        embed = discord.Embed(
            title=":alarm_clock: Reminder Arrived",
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(
            name="Content:",
            value=reminder['content'][:50],
            inline=False
        )
        embed.add_field(
            name="Original Message:",
            value=f"[here]({reminder['jump_url']}).",
            inline=False
        )

        embed.timestamp = datetime.utcnow()

        # taken from discord.Message.raw_mentions()
        mentions = [f"<@{x}>" for x in re.findall(r'<@!?([0-9]+)>', reminder["content"])]
        mentions.append(user.mention)
        mentions = ", ".join(mentions)

        await channel.send(content=mentions, embed=embed)

        await db_execute(
            self.bot.db_pool,
            "DELETE FROM reminders WHERE reminder_id=$1",
            reminder["reminder_id"]
        )

        del self.reminders[reminder["reminder_id"]]
        await self.schedule_reminder(self.get_recent_reminder())

    @group(name="remind", aliases=("reminder",), invoke_without_command=True)
    async def remind_group(self, ctx: Context, duration: str, *, content: str) -> None:
        """
        Set reminders.

        syntax: !remind <duration> <message>
        Accepted duration formats:
            - d|day|days
            - h|hour|hours
            - m|min|mins|minute|minutes
            - s|sec|secs|second|seconds

        Example:
            !remind 1hour drink water
            !remind 10m submit assignment
            !remind 1hour30min workout
            !remind 20days1hour20min my birthday
        """
        await self.remind_duration(ctx, duration, content=content)

    async def append_reminder(self, timestamp: datetime, ctx: Context, content: str) -> None:
        """Add reminder to database and schedule it."""
        sql = (
            "INSERT INTO reminders(jump_url, user_id, channel_id, end_time, content) "
            "VALUES ($1, $2, $3, $4, $5)RETURNING reminder_id"
        )
        async with self.bot.db_pool.acquire() as connection:
            reminder_id = await connection.fetchval(
                sql, ctx.message.jump_url, ctx.author.id, ctx.channel.id, timestamp, content
            )

        embed = Embed()
        embed.title = "Reminder set"
        embed.description = REMINDER_DESCRIPTION.format(
            reminder_id=reminder_id,
            arrive_in=humanize.precisedelta(timestamp - datetime.utcnow(), format="%0.0f"),
            content=content
        )
        await ctx.send(embed=embed)
        self.reminders[reminder_id] = {
            "reminder_id": reminder_id,
            "jump_url": ctx.message.jump_url,
            "user_id": ctx.author.id,
            "channel_id": ctx.channel.id,
            "end_time": timestamp,
            "content": content,
        }

        await self.schedule_reminder(self.get_recent_reminder())

    async def remind_duration(
        self, ctx: Context, duration: str, *, content: str
    ) -> None:
        """Set reminder base on duration."""
        future_timestamp = parse_duration(duration)
        if not future_timestamp:
            await ctx.send("Invalid duration!")
            return
        await self.append_reminder(future_timestamp, ctx, content)

    @remind_group.command(name="list", aliases=("l",))
    async def list_reminders(self, ctx: Context):
        """List all your reminders."""
        reminders = [
            reminder for reminder in self.reminders.values() if reminder["user_id"] == ctx.author.id
        ]
        lines = [
            f"**{i}.** `ID: {reminder['reminder_id']}` - arrives in "
            f"**{humanize.precisedelta(reminder['end_time'] - datetime.utcnow(), format='%0.0f')}**\n"
            f"{reminder['content']}\n"
            for i, reminder in enumerate(reminders, start=1)
        ]
        embed = Embed()
        embed.title = "Your reminders :hourglass:"
        embed.timestamp = datetime.utcnow()

        await LinePaginator.paginate(
            lines,
            ctx,
            embed,
            allow_empty_lines=True,
        )

    @remind_group.command(name="delete", aliases=("d", "del"))
    async def delete_reminder(self, ctx: Context, reminder_id: int):
        """Delete scheduled reminder."""
        if reminder_id in self.reminders:
            await db_execute(
                self.bot.db_pool,
                "DELETE FROM reminders WHERE reminder_id=$1 and user_id=$2;",
                reminder_id,
                ctx.author.id
            )
            del self.reminders[reminder_id]
            if self.current_scheduled == reminder_id:
                await self.cancel_reminder_task()
                await self.schedule_reminder(self.get_recent_reminder())
            await ctx.send("reminder deleted successfully !")

        else:
            await ctx.send(f"Reminder with ID: {reminder_id} not found!")


def setup(bot: Bot) -> None:
    """Init cog."""
    bot.add_cog(Reminder(bot))
