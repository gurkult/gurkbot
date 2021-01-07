import os

from discord import Embed
from discord.ext import commands
from loguru import logger

from . import constants


class Bot(commands.Bot):
    """The core of the bot."""

    def __init__(self) -> None:

        intents = Intents.default()
        intents.members = True

        super().__init__(command_prefix=constants.PREFIX, intents=intents)
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
            name="Gurkbot",
            url=constants.BOT_REPO_URL,
            icon_url=self.user.avatar_url,
        )
        await self.get_channel(constants.Channels.devlog).send(embed=embed)
