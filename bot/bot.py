import os
from typing import Optional

from aiohttp import ClientSession
from bot.postgres import db_init
from discord import Embed, Intents
from discord.ext import commands
from loguru import logger
from tortoise import Tortoise

from . import constants


class Bot(commands.Bot):
    """The core of the bot."""

    def __init__(self) -> None:
        intents = Intents.default()
        intents.members = True
        intents.presences = True

        self.http_session = ClientSession()

        super().__init__(command_prefix=constants.PREFIX, intents=intents)

        self.loop.create_task(self._db_setup())

        self.load_extensions()

    async def _db_setup(self) -> None:
        """Setup and initialize database connection."""
        try:
            await db_init()
        except Exception as e:
            logger.info("Initializing database...FAILED...closing bot connection.")
            await self.wait_until_ready()
            error_msg = f"**{e.__class__.__name__}**\n```{e}```"
            embed = Embed(
                title="Database error",
                description=error_msg,
                colour=constants.Colours.soft_red,
            )

            await self.notify_dev_alert(embed=embed)
            await self.close()

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

    async def notify_dev_alert(
        self, content: Optional[str] = None, embed: Optional[Embed] = None
    ) -> None:
        """Notify dev alert channel."""
        await self.get_channel(constants.Channels.devalerts).send(
            content=content, embed=embed
        )

    async def close(self) -> None:
        """Close Http session when bot is shutting down."""
        if self.http_session:
            await self.http_session.close()

        await Tortoise.close_connections()
        await super().close()
