from aiogram.types import Message
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import is_redis_hexists_tracker
from cache.redis_schedule_command import redis_sadd_user_id, is_redis_sismember_user
from db.users.users_commands import create_user
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import start_menu_inline_kb
from tgbot.utils.answer_text import user_in_db_text, new_user_text, started_tracker_text


async def command_start_handler(message: Message, db_session: async_sessionmaker[AsyncSession], redis_client: Redis,
                                buttons: AppButtons) -> Message:
    """
    The command_start_handler function is the first function that a user interacts with when they start using the bot.
    It checks if a user is already in the database and cache, and if not it adds them to both. It also checks whether or not
    the user has started tracking their time, and returns an appropriate message based on this.

    :param message: Message: Get the user id and username
    :param db_session: async_sessionmaker[AsyncSession]: Access the database
    :param redis_client: Redis: Access the redis database
    :param buttons: AppButtons: Get the buttons from the middleware
    :return: The message text and the keyboard
    """
    user_id: int = message.from_user.id
    await message.delete()
    user_from_cache: bool = await is_redis_sismember_user(user_id, redis_client)
    # Get keyboard
    markup = await start_menu_inline_kb(await buttons.main_menu_buttons())
    # Check if sender already in DB
    if user_from_cache:
        if await is_redis_hexists_tracker(user_id, redis_client):
            started_text = await started_tracker_text(user_id, redis_client)
            return await message.answer(text=started_text, reply_markup=markup)
        else:
            return await message.answer(text=user_in_db_text, reply_markup=markup)
    else:
        # Add a new user to the cache
        await redis_sadd_user_id(user_id, redis_client)
        # Add a new user to the database
        await create_user(
            user_id=user_id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            db_session=db_session
        )
        return await message.answer(text=new_user_text, reply_markup=markup)
