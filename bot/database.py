import asyncpg

# import aioredis
from datetime import datetime

from bot.config_data.config import load_config

config = load_config()
DATABASE_URL = (
    f"postgresql://{config.db.DB_USER}:{config.db.DB_password}@"
    f"{config.db.DB_HOST}/{config.db.DATABASE}"
)

# REDIS_URL = "redis://localhost"


async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)


async def get_user(pool, user_id):
    async with pool.acquire() as connection:
        return await connection.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )


async def add_user(pool, user_id, username, first_name, last_name):
    async with pool.acquire() as connection:
        await connection.execute(
            """
            INSERT INTO users (user_id, username, first_name, last_name, 
            created_at)
            VALUES ($1, $2, $3, $4, $5)
        """,
            user_id,
            username,
            first_name,
            last_name,
            datetime.now(),
        )


async def get_rate_for_date(pool, date):
    async with pool.acquire() as connection:
        result = await connection.fetchrow(
            "SELECT rate FROM keyratecbr WHERE date <= $1 ORDER BY date DESC "
            "LIMIT 1",
            date,
        )
        return result if result else None


# async def create_redis_pool():
#     return await aioredis.create_redis_pool(REDIS_URL)
