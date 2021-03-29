import asyncio
import random
from datetime import datetime, time, timedelta
from typing import List

from bot import constants
from bot.converters import OffTopicName as OT_Converter
from bot.postgres.models import OffTopicName as OT_Model
from discord import TextChannel
from discord.ext.commands import Bot, Cog, Context, group
from loguru import logger


class OffTopicNames(Cog):
    """Manage off-topic channel names."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.ot_channel: TextChannel = self.bot.get_channel(
            constants.Channels.off_topic
        )
        self.ot_names: List[OT_Model] = ...

        self.bot.loop.create_task(self.cache_otn_names())
        self.bot.loop.create_task(self.update_ot_channel_name())

    async def cache_otn_names(self) -> None:
        """Get all off topic channel names."""
        self.ot_names = await OT_Model.all().values_list("name", flat=True)

    @group(name="offtopicnames", aliases=("otn",), invoke_without_command=True)
    async def off_topic_names(self, ctx: Context) -> None:
        """Commands for managing off-topic-channel names."""
        await ctx.send_help(ctx.command)

    @off_topic_names.command(name="add", aliases=("a",))
    async def add_ot_name(self, ctx: Context, *, name: OT_Converter) -> None:
        """Add off topic channel name."""
        ot_ins = await OT_Model.create(name=name)
        self.ot_names.append(ot_ins)

        await ctx.send(f"`{name}` has been added!")

    @off_topic_names.command(name="del", aliases=("remove", "delete"))
    async def delete_ot_name(self, ctx: Context, *, name: OT_Converter) -> None:
        """Delete off topic channel name."""
        otn_instance = (
            await OT_Model.filter(name=name) if OT_Model.exists(name=name) else None
        )

        if not otn_instance:
            await ctx.send(f"`{name}` not found!")
            return

        await otn_instance[0].delete()
        self.ot_names.remove(name)

        await ctx.send(f"`{name}` has been deleted!")

    async def update_ot_channel_name(self) -> None:
        """Update ot-channel name everyday at midnight."""
        while not self.bot.is_closed():
            now = datetime.utcnow()
            midnight_datetime = datetime.combine(
                now.date() + timedelta(days=1), time(0)
            )
            till_midnight = int((midnight_datetime - now).total_seconds())
            logger.info(
                f"Sleeping till {till_midnight} before re-naming off topic channel."
            )
            await asyncio.sleep(till_midnight)

            name = self.ot_channel.name
            while name == self.ot_channel.name:
                name = random.choice(self.ot_names)

            await self.ot_channel.edit(name=name)
            logger.info(f"Off-topic Channel name changed to {name}.")


def setup(bot: Bot) -> None:
    """Load cog."""
    bot.add_cog(OffTopicNames(bot))
