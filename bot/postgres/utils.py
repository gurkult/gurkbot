from typing import List

from asyncpg import Pool, Record
from loguru import logger


async def db_execute(pool: Pool, sql_statement: str, *args) -> None:
    """Execute SQL statement."""
    async with pool.acquire() as connection:
        logger.info(f"Executing SQL: {sql_statement}")
        logger.info(f"with args: {args}")
        status = await connection.execute(sql_statement, *args)
    logger.info(f"DB execute status: {status}")


async def db_fetch(pool: Pool, sql_statement: str, *args) -> List[Record]:
    """Execute SQL statement."""
    async with pool.acquire() as connection:
        result = await connection.fetch(
            sql_statement,
            *args,
        )

    return result
