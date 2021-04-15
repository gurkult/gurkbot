from bot.constants import DATABASE_URL
from loguru import logger
from tortoise import Tortoise


async def db_init() -> None:
    """Initialize database connection and create tables."""
    logger.info("Initializing database...")
    await Tortoise.init(
        db_url=DATABASE_URL, modules={"models": ["bot.postgres.models"]}
    )
    # Generate the schema
    await Tortoise.generate_schemas(safe=True)

    logger.info("Initializing database...DONE")
