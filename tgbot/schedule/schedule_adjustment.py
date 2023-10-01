from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler_di import ContextSchedulerDecorator
from redis.asyncio import Redis


async def setup_scheduler(bot: Bot, jobstores: dict[str, int], storage: RedisStorage,
                          redis_client: Redis, async_session: async_sessionmaker[AsyncSession],
                          # t_hub: TranslatorHub
                          ) -> ContextSchedulerDecorator:
    """
    The setup_scheduler function is a factory function that returns an instance of the ContextSchedulerDecorator class.

    :param bot: Bot: Pass the bot instance to the scheduler
    :param jobstores: dict[str: Define the type of jobstore that is used
    :param dict[str, int]: Specify the type of jobstores
    :param storage: RedisStorage: Store the data in redis
    :param redis_client: Redis: Create a redis instance
    :param async_session: async_sessionmaker[AsyncSession]: Create a database session
    :return: A contextschedulerdecorator object
    """
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=jobstores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.ctx.add_instance(scheduler, declared_class=BaseScheduler)
    scheduler.ctx.add_instance(storage, declared_class=RedisStorage)
    scheduler.ctx.add_instance(redis_client, declared_class=Redis)
    # i18n = t_hub.get_translator_by_locale(settings.EN_LANG_CODE)
    # scheduler.ctx.add_instance(i18n, declared_class=TranslatorRunner)
    async with async_session() as session:
        scheduler.ctx.add_instance(session, declared_class=async_sessionmaker[AsyncSession])

    return scheduler
