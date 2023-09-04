from functools import lru_cache

from aiogram import Bot
from aiogram.fsm.storage import redis
from redis.asyncio.client import Redis

from configuration import Settings


@lru_cache()
def get_settings():
    return Settings()


# Get data from .env
settings = get_settings()
# Initialize bot
BOT = Bot(settings.BOT_TOKEN, parse_mode='HTML')

DB_URL = settings.db_url

pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)
redis_client = Redis(connection_pool=pool)

LENGTH_NAME_LIMIT = 20
USER_ACTIONS_LIMIT = 10
USER_CATEGORIES_LIMIT = 10
