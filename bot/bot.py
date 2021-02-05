from aiohttp import ClientSession
from discord import Embed
from discord.ext import commands
from loguru import logger

from . import constants


class Bot(commands.Bot):
    """The core of the bot."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.http_session = ClientSession()

    def load_extensions(self) -> None:
        """Load all the extensions in the exts/ folder."""
        # importing here to avoid ciricular import
        from bot.utils.extension import EXTENSIONS

        logger.info("Start loading extensions from bot/exts/")

        for ext in EXTENSIONS:
            self.load_extension(ext)
            logger.info(f"Successfully loaded extension: {ext}")

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
        await super().close()

        if self.http_session:
            await self.http_session.close()
