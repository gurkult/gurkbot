import os
from datetime import datetime
from typing import Optional

import asyncpg
from aiohttp import ClientSession
from bot.postgres import create_tables
from discord import AllowedMentions, Embed, Intents, Object
from discord.ext import commands
from loguru import logger

from . import constants


class Bot(commands.Bot):
    """The core of the bot."""

    def __init__(self) -> None:
        intents = Intents.default()
        intents.members = True
        intents.presences = True

        self.http_session = ClientSession()
        self.db_pool: asyncpg.Pool = asyncpg.create_pool(constants.DATABASE_URL)
        roles = [
            Object(r)
            for r in [
                constants.Roles.steering_council,
                constants.Roles.moderators,
                constants.Roles.gurkult_lords,
            ]
        ]

        super().__init__(
            command_prefix=constants.PREFIX,
            intents=intents,
            allowed_mentions=AllowedMentions(
                everyone=None,
                users=True,
                roles=roles,
                replied_user=True,
            ),
        )

        self.loop.create_task(self._db_setup())

        self.launch_time = datetime.utcnow().timestamp()

    async def notify_dev_alert(
        self, content: Optional[str] = None, embed: Optional[Embed] = None
    ) -> None:
        """Notify dev alert channel."""
        await self.wait_until_ready()
        await self.get_channel(constants.Channels.devalerts).send(
            content=content, embed=embed
        )

    async def _db_setup(self) -> None:
        """Setup and initialize database connection."""
        try:
            await self.db_pool
            await create_tables(self.db_pool)
        except Exception as e:
            error_msg = f"**{e.__class__.__name__}**\n```{e}```"
            logger.error(f"Database ERROR: {error_msg}")

            await self.notify_dev_alert(
                embed=Embed(
                    title="Database error",
                    description=error_msg,
                    colour=constants.Colours.soft_red,
                )
            )
            await self.close()

        self.load_extensions()

    def load_extensions(self) -> None:
        """Load all the extensions in the exts/ folder."""
        logger.info("Start loading extensions from ./exts/")
        for extension in constants.EXTENSIONS.glob("*/*.py"):
            if extension.name.startswith("_"):
                continue  # ignore files starting with _
            dot_path = str(extension).replace(os.sep, ".")[:-3]  # remove the .py
            self.load_extension(dot_path)
            logger.info(f"Successfully loaded extension:  {dot_path}")

    def run(self) -> None:
        """Run the bot with the token in constants.py/.env ."""
        logger.info("Starting bot")

        if constants.TOKEN is None:
            raise EnvironmentError(
                "token value is None. Make sure you have configured the TOKEN field in .env"
            )

        super().run(constants.TOKEN)

    async def on_ready(self) -> None:
        """Ran when the bot has connected to discord and is ready."""
        logger.info("Bot online")
        await self.startup_greeting()

    async def startup_greeting(self) -> None:
        """Announce presence to the devlog channel."""
        embed = Embed(description="Connected!")
        embed.set_author(
            name="Gurkbot", url=constants.BOT_REPO_URL, icon_url=self.user.avatar_url
        )
        await self.get_channel(constants.Channels.devlog).send(embed=embed)

    async def close(self) -> None:
        """Close Http session when bot is shutting down."""
        if self.http_session:
            await self.http_session.close()

        if self.db_pool:
            await self.db_pool.close()

        await super().close()
