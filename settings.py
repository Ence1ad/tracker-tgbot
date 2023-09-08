from aiogram import Bot
from aiogram.fsm.storage import redis
from redis.asyncio import ConnectionPool
from redis.asyncio.client import Redis
from apscheduler.jobstores.redis import RedisJobStore

from config import settings

# Initialize bot
BOT: Bot = Bot(settings.BOT_TOKEN, parse_mode='HTML')

DB_URL: str = settings.db_url

pool: ConnectionPool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    max_connections=10
)
redis_client: Redis = Redis(connection_pool=pool)

scheduler_jobstores = {
    'default': RedisJobStore(
        jobs_key='dispatched_trips_jobs',
        run_times_key='dispatched_trips_running',
        host=settings.REDIS_HOST,
        db=settings.REDIS_DB,
        port=settings.REDIS_PORT
    )
}

LOGGING_LEVEL = settings.LEVEL

LENGTH_NAME_LIMIT: int = 20
USER_ACTIONS_LIMIT: int = 10
USER_CATEGORIES_LIMIT: int = 10
USER_WEEK_TRACKERS_LIMIT: int = 100
MAX_HOURS_DURATION_TRACKER: int = 1
