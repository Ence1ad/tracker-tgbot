from functools import lru_cache

from aiogram import Bot
from aiogram.fsm.storage import redis
from redis.asyncio.client import Redis
from sqlalchemy import URL

from config import Settings


@lru_cache()
def get_settings():
    return Settings()


# Get data from .env
settings = get_settings()
# Initialize bot
BOT = Bot(settings.tgbot.bot_token, parse_mode='HTML')

# Database credentials
DB_URL = URL.create(
    drivername=f"postgresql+asyncpg",
    username=settings.postgres.pg_user,
    password=settings.postgres.pg_password,
    host=settings.postgres.pg_host,
    port=settings.postgres.pg_port,
    database=settings.postgres.db_name
).render_as_string()


pool = redis.ConnectionPool(
    host=settings.redis.redis_host,
    port=settings.redis.redis_port,
    db=settings.redis.redis_db
)
redis_client = Redis(connection_pool=pool)
CACHE = ...

LENGTH_ACTION_NAME_LIMIT = 20
USER_ACTIONS_LIMIT = 10
TIME_ZONE_OFFSET = 3
