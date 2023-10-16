from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler_di import ContextSchedulerDecorator
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def setup_scheduler(
        bot: Bot, jobstores: dict[str, int], storage: RedisStorage, redis_client: Redis,
        async_session: async_sessionmaker[AsyncSession],
) -> ContextSchedulerDecorator:
    """Set up and configure an asynchronous scheduler with context support.

    This function configures and initializes an asynchronous scheduler using the
    `APScheduler` library. It associates the scheduler with a specific `bot`, jobstores,
     Redis storage, and an async session for database operations.


    :param bot: An instance of the `aiogram.Bot` class.
    :param jobstores: dict[str, int]: A dictionary specifying jobstores for the
    scheduler.
    :param storage: RedisStorage: Redis storage for the scheduler's job execution
    state.
    :param redis_client: An instance of the `redis.asyncio.Redis` client.
    :param async_session:  (async_sessionmaker[AsyncSession]): An async session maker
    for database interactions.
    :return: ContextSchedulerDecorator: A decorated asynchronous scheduler instance
    configured with context support.
    """
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=jobstores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.ctx.add_instance(scheduler, declared_class=BaseScheduler)
    scheduler.ctx.add_instance(storage, declared_class=RedisStorage)
    scheduler.ctx.add_instance(redis_client, declared_class=Redis)
    async with async_session() as session:
        scheduler.ctx.add_instance(session,
                                   declared_class=async_sessionmaker[AsyncSession])

    return scheduler
