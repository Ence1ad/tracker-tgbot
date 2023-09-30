from aiogram.types import ChatMemberUpdated, Message
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from cache.redis_schedule_command import redis_sadd_user_id, redis_srem_user_id
from db.users.users_commands import delete_user, create_user


async def add_user_handler(event: ChatMemberUpdated, redis_client: Redis, db_session: async_sessionmaker[AsyncSession]
                           ) -> Message:
    """
    The add_user_handler function is a handler for the ChatMemberUpdated event.
    It adds a new user to the database and cache when they join the group chat.

    :param event: ChatMemberUpdated: Get the user's id, first name, last name and username
    :param redis_client: Redis: Get the redis client from the middleware
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
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
    msg = await event.answer(f"{first_name} Добро пожаловать в группу!")
    return msg


async def remove_user_handler(event: ChatMemberUpdated, redis_client: Redis,
                              db_session: async_sessionmaker[AsyncSession]) -> Message:
    """
    The remove_user_handler function is a handler for the ChatMemberUpdated event.
    It removes the user from Redis and deletes their data from PostgreSQL db.


    :param event: ChatMemberUpdated: Get the user id of the removed user
    :param redis_client: Redis: Get the redis client from the middleware
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :return: A message that the user was removed from the group
    """
    user_id = event.new_chat_member.user.id
    await redis_srem_user_id(user_id, redis_client)
    await delete_user(user_id, db_session)
    msg = await event.answer(f"{event.new_chat_member.user.first_name} был(а) удален(а) из группы!")
    return msg
