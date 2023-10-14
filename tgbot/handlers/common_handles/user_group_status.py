import shutil
from pathlib import Path

from aiogram.types import ChatMemberUpdated, Message
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from cache.users_redis_manager import redis_sadd_user_id, redis_srem_user_id
from config import settings
from db.operations.users_operations import delete_user, create_user


async def add_user_handler(event: ChatMemberUpdated, redis_client: Redis,
                           db_session: AsyncSession, i18n: TranslatorRunner
                           ) -> Message:
    """
    Handle the event of adding a user to the group.

    :param event: ChatMemberUpdated: The update event triggered by the user's addition.
    :param redis_client: Redis: The Redis client for caching user information.
    :param db_session: AsyncSession: The database session.
    :param i18n: TranslatorRunner: The translator runner for localization.
    :return: Message: The welcome message sent to the added user.
    """
    user_id: int = event.new_chat_member.user.id
    first_name: str = event.new_chat_member.user.first_name
    last_name: str | None = event.new_chat_member.user.last_name
    username: str | None = event.new_chat_member.user.username
    # Add a new user to the db and cache
    await redis_sadd_user_id(user_id, redis_client)
    await create_user(user_id=user_id, first_name=first_name, last_name=last_name,
                      username=username, db_session=db_session)
    msg = await event.answer(f"{first_name} {i18n.get('welcome_group_text')}")
    return msg


async def remove_user_handler(event: ChatMemberUpdated, redis_client: Redis,
                              i18n: TranslatorRunner, db_session: AsyncSession
                              ) -> Message:
    """
    Handle the event of removing a user from the group.

    :param event: ChatMemberUpdated: The update event triggered by the user's removal.
    :param redis_client: Redis: The Redis client for caching user information.
    :param i18n: TranslatorRunner: The translator runner for localization.
    :param db_session: AsyncSession: The database session.
    :return: Message: The farewell message sent to the removed user.
    """
    user_id: int = event.new_chat_member.user.id
    await redis_srem_user_id(user_id, redis_client)
    await delete_user(user_id, db_session)
    if Path.exists(Path(f'{settings.USER_REPORT_DIR}{user_id}')):
        shutil.rmtree(Path(f'{settings.USER_REPORT_DIR}{user_id}'))
    return await event.answer(f"{event.new_chat_member.user.first_name} "
                              f"{i18n.get('farewell_group_text')}")
