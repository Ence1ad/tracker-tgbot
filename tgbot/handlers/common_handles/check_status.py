import shutil
from pathlib import Path

from aiogram.types import ChatMemberUpdated, Message
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from cache.users_redis_manager import redis_sadd_user_id, redis_srem_user_id
from config import settings
from db.operations.users_operations import delete_user, create_user


async def add_user_handler(event: ChatMemberUpdated, redis_client: Redis, db_session: async_sessionmaker[AsyncSession],
                           i18n: TranslatorRunner) -> Message:
    """
    Adds a new user to the database and cache when they join the group chat.

    :param event: ChatMemberUpdated: Get the user's id, first name, last name and username
    :param redis_client: Redis: Get the redis client from the middleware
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: Greeting message
    """
    user_id: int = event.new_chat_member.user.id
    first_name: str = event.new_chat_member.user.first_name
    last_name: str = event.new_chat_member.user.last_name
    username: str = event.new_chat_member.user.username
    # Add a new user to the db and cache
    await create_user(user_id=user_id, first_name=first_name, last_name=last_name, username=username,
                      db_session=db_session)
    await redis_sadd_user_id(user_id, redis_client)
    msg = await event.answer(f"{first_name} {i18n.get('welcome_group_text')}")
    return msg


async def remove_user_handler(event: ChatMemberUpdated, redis_client: Redis, i18n: TranslatorRunner,
                              db_session: async_sessionmaker[AsyncSession]) -> Message:
    """
    Removes the user from Redis and deletes their data from PostgreSQL db. Also delete user's reports

    :param event: ChatMemberUpdated: Get the user id of the removed user
    :param redis_client: Redis: Get the redis client from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :return: A message that the user was removed from the group
    """
    user_id = event.new_chat_member.user.id
    await redis_srem_user_id(user_id, redis_client)
    await delete_user(user_id, db_session)
    if Path.exists(Path(f'{settings.USER_REPORT_DIR}{user_id}')):
        shutil.rmtree(Path(f'{settings.USER_REPORT_DIR}{user_id}'))
    msg = await event.answer(f"{event.new_chat_member.user.first_name} {i18n.get('farewell_group_text')}")
    return msg
