import asyncio
import datetime
import random
from typing import Dict, Iterable, List

from disnake import Embed, Reaction, TextChannel, User
from disnake.ext import tasks
from disnake.ext.commands import Cog, Context, group, has_any_role
from fuzzywuzzy import fuzz
from loguru import logger

from bot import constants
from bot.bot import Bot
from bot.converters import OffTopicName as OT_Converter
from bot.postgres.utils import db_execute, db_fetch
from bot.utils.pagination import LinePaginator

FUZZ_RATIO = 80
FUZZ_PARTIAL_RATIO = 100
OT_NAME_PREFIX = "ot｜"
REFRESH_TIMES = [
    datetime.time(hour=0, minute=0, second=0),
    datetime.time(hour=12, minute=0, second=0),
]


class OffTopicNames(Cog):
    """Manage off-topic channel names."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.ot_channel: TextChannel = ...
        self.ot_names: Dict[str:int] = ...
        """Key is off-topic channel name, value is times used."""

        self.bot.loop.create_task(self._cache())
        self.update_ot_channel_name.start()

    def cog_unload(self) -> None:
        """Cancels all tasks upon unload."""
        self.update_ot_channel_name.cancel()

    async def _cache(self) -> None:
        """Get all off topic channel names."""
        await self.bot.wait_until_ready()

        self.ot_channel: TextChannel = self.bot.get_channel(
            constants.Channels.off_topic
        )
        self.ot_names = dict(
            await db_fetch(self.bot.db_pool, "SELECT * FROM offtopicnames")
        )

    def _find(self, name: OT_Converter) -> List[str]:
        """Find similar Off-topic names."""
        return [
            ot_name
            for ot_name in self.ot_names
            if fuzz.ratio(ot_name, name) > FUZZ_RATIO
            or fuzz.partial_ratio(ot_name, name) == FUZZ_PARTIAL_RATIO
        ]

    @staticmethod
    def _find_embed_builder(ot_names: List[str], title: str) -> Embed:
        """Build embed with a list of Off Topic names."""
        return Embed(
            title=title,
            description=(
                "\n".join(
                    f"{i}. {ot_name}" for i, ot_name in enumerate(ot_names, start=1)
                )
                if ot_names
                else ":x: 0 Matches found."
            ),
            colour=constants.Colours.green if ot_names else constants.Colours.soft_red,
        )

    @staticmethod
    async def _send_paginated_embed(
        ctx: Context, lines: Iterable[str], title: str
    ) -> None:
        """Send paginated embed."""
        embed = Embed()
        embed.set_author(name=title)
        await LinePaginator.paginate(
            [f"{i}. {line}" for i, line in enumerate(lines, start=1)],
            ctx,
            embed,
            allow_empty_lines=True,
        )

    @staticmethod
    async def _send_ot_embed(
        channel: TextChannel,
        description: str,
        positive: bool,
        title: str = "Off Topic Names",
    ) -> None:
        """Embed helper for Off Topic Names cog."""
        embed = Embed(
            title=title,
            description=description,
            colour=constants.Colours.green if positive else constants.Colours.soft_red,
        )
        await channel.send(embed=embed)

    @group(name="offtopicnames", aliases=("otn",), invoke_without_command=True)
    async def off_topic_names(self, ctx: Context) -> None:
        """Commands for managing off-topic-channel names."""
        await ctx.send_help(ctx.command)

    @off_topic_names.command(name="add", aliases=("a",))
    async def add_ot_name(self, ctx: Context, *, name: OT_Converter) -> None:
        """Add off topic channel name."""
        if name in self.ot_names:
            await self._send_ot_embed(
                ctx.channel, f":x:`{name}` already exists!", False
            )
            return

        similar_names = self._find(name)

        if similar_names:
            embed = self._find_embed_builder(
                similar_names[:5], "Found similar existing names :name_badge:"
            )
            embed.set_footer(text="Do you still want to add the off topic name?")
            confirmation_msg = await ctx.send(embed=embed)

            await confirmation_msg.add_reaction(constants.Emojis.CHECK_MARK_EMOJI)
            await confirmation_msg.add_reaction(constants.Emojis.CROSS_MARK_EMOJI)

            def check(reaction: Reaction, user: User) -> bool:
                return reaction.message == confirmation_msg and user == ctx.author

            async def _exit() -> None:
                await confirmation_msg.delete()
                await self._send_ot_embed(
                    ctx.channel, f"Off topic name `{name}` not added.", False
                )

            try:
                reaction, _ = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=60.0
                )
            except asyncio.TimeoutError:
                return await _exit()

            if str(reaction.emoji) == constants.Emojis.CROSS_MARK_EMOJI:
                return await _exit()

        await db_execute(
            self.bot.db_pool, "INSERT INTO offtopicnames VALUES ($1)", name
        )
        self.ot_names[name] = 0

        await self._send_ot_embed(
            ctx.channel, f"`{name}` has been added :ok_hand:", True
        )

    @off_topic_names.command(name="delete", aliases=("d", "r", "remove"))
    async def delete_ot_name(self, ctx: Context, *, name: OT_Converter) -> None:
        """Delete off topic channel name."""
        if name not in self.ot_names:
            await self._send_ot_embed(ctx.channel, f":x: `{name}` not found!", False)
            if names := self._find(name):
                await self._send_paginated_embed(
                    ctx, names, "Did you mean one of the following?"
                )
            return

        await db_execute(
            self.bot.db_pool, "DELETE FROM offtopicnames WHERE name=$1", name
        )
        del self.ot_names[name]

        await self._send_ot_embed(
            ctx.channel, f"`{name}` has been deleted :white_check_mark:", True
        )

    @off_topic_names.command(name="find", aliases=("f", "s", "search"))
    async def find_ot_name(self, ctx: Context, *, name: OT_Converter) -> None:
        """Find similar off-topic names in database."""
        await self._send_paginated_embed(
            ctx,
            self._find(name),
            f"{constants.Emojis.MAG_RIGHT_EMOJI} Search result: {name}",
        )

    @off_topic_names.command(name="list", aliases=("l",))
    async def list_ot_names(self, ctx: Context) -> None:
        """List all Off Topic names."""
        await self._send_paginated_embed(ctx, self.ot_names.keys(), "Off Topic Names")

    @tasks.loop(time=REFRESH_TIMES)
    async def update_ot_channel_name(self) -> None:
        """Update ot-channel name everyday at `REFRESH_TIMES`."""
        # await the cache method to ensure we pull from an up-to-date cache every time
        # this also fixes a race condition where the cache wasn't populated
        await self._cache()
        # Algorithm to select next off topic name based on usage/number of times the name has been used.
        # Least used names have a higher chance of being selected.
        usage = set(self.ot_names.values())
        distribution = [1 / (i + 1) for i in usage]
        chosen_usage = random.choices(list(usage), distribution)[0]

        chosen_ot_names: set[str] = {
            name for name, usage in self.ot_names.items() if usage == chosen_usage
        }

        def to_channel_name(ot_name: str) -> str:
            """Append off topic name prefix."""
            return f"{OT_NAME_PREFIX}{ot_name}"

        def from_channel_name(ot_name: str) -> str:
            """Detach off topic name prefix."""
            return ot_name.removeprefix(OT_NAME_PREFIX)

        current_name = from_channel_name(self.ot_channel.name)

        chosen_ot_names.discard(current_name)
        new_name = random.choice(list(chosen_ot_names))

        self.ot_names[new_name] += 1
        await db_execute(
            self.bot.db_pool,
            "UPDATE offtopicnames SET num_used=num_used+1 WHERE name=$1",
            new_name,
        )

        new_name_with_prefix = to_channel_name(new_name)
        await self.ot_channel.edit(name=new_name_with_prefix)

        await self._send_ot_embed(
            self.ot_channel, new_name, True, "New Off-Topic Name!"
        )
        logger.info(f"Off-topic Channel name changed to {new_name}.")

    async def cog_check(self, ctx: Context) -> bool:
        """Check if user is gurkult lord or mod."""
        return await has_any_role(
            constants.Roles.moderators, constants.Roles.gurkult_lords
        ).predicate(ctx)


def setup(bot: Bot) -> None:
    """Load cog."""
    bot.add_cog(OffTopicNames(bot))
