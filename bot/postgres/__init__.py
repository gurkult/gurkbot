from pathlib import Path

from asyncpg import Pool


async def create_tables(pool: Pool) -> None:
    """Execute all sql files inside /tables folder."""
    tables_path = Path("bot", "postgres", "tables")
    async with pool.acquire() as connection:
        async with connection.transaction():
            for table_file in tables_path.iterdir():
                await connection.execute(table_file.read_text())
