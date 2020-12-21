from discord.ext import commands
from loguru import logger

from . import constants


class Bot(commands.Bot):
    """The core of the bot."""

    def __init__(self) -> None:
        super().__init__(command_prefix=constants.PREFIX)
        self.load_extensions()

    def load_extensions(self) -> None:
        """Load all the extensions in the exts/ folder."""
        logger.info('Start loading extensions from ./exts/')
        for extension in constants.EXTENIONS.glob("*/*.py"):
            dot_path = str(extension).replace("/", ".")[:-3]  # remove the .py
            if "__init__" in dot_path:  # the __init__.py
                continue

            self.load_extension(dot_path)
            logger.info(f"Successfully loaded extension:  {dot_path}")

    def run(self) -> None:
        """Run the bot with the token in constants.py/.env ."""
        logger.info("Starting bot")
        super().run(constants.TOKEN)

    async def on_ready(self) -> None:
        """Ran when the bot has connected to discord and is ready."""
        logger.info("Bot online")
