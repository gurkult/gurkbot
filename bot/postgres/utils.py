from typing import List

from asyncpg import Pool, Record
from loguru import logger


async def db_execute(pool: Pool, sql_statement: str, *args) -> bool:
    """
    Execute SQL statement.

    Use CREATE, DELETE, INSERT, and UPDATE.
    """
    async with pool.acquire() as connection:
        async with connection.transaction():
            logger.info(f"Executing SQL: {sql_statement}")
            logger.info(f"with args: {args}")
            status = await connection.execute(sql_statement, *args)
    logger.info(f"DB execute status: {status}")


async def db_fetch(pool: Pool, sql_statement: str, *args) -> List[Record]:
    """
    Excute SQL statement.

    Use for SELECT.
    """
    async with pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetch(
                sql_statement,
                *args,
            )
    return result
