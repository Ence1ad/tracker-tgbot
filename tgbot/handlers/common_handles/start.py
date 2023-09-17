from aiogram.types import Message
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import is_redis_hexists_tracker
from cache.redis_schedule_command import redis_sadd_user_id, is_redis_sismember_user
from db.users.users_commands import create_user
from tgbot.keyboards.buttons_names import start_menu_buttons
from tgbot.keyboards.inline_kb import start_menu_inline_kb
from tgbot.utils.answer_text import user_in_db_text, new_user_text, launch_tracker_text, started_tracker_text


async def command_start_handler(message: Message, db_session: async_sessionmaker[AsyncSession], redis_client: Redis) -> None:
    """
    Function react to tap on "/start" command. Function check if user exist in db,
    function just return some answer as message, else create user in db and return answer as message.
    :param message: Message
    :param db_session: AsyncSession
    :param redis_client: Redis
    :return: Coroutine[Any]
    """
    user_id: int = message.from_user.id
    await message.delete()
    user_from_cache: bool = await is_redis_sismember_user (user_id, redis_client)
    # Get keyboard
    start_markup = await start_menu_inline_kb(start_menu_buttons)
    # Check if sender already in DB
    if user_from_cache:
        if await is_redis_hexists_tracker(user_id, redis_client):
            started_text = await started_tracker_text(user_id, redis_client)
            await message.answer(text=launch_tracker_text + started_text, reply_markup=start_markup)
        else:
            await message.answer(text=user_in_db_text, reply_markup=start_markup)
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
        await message.answer(text=new_user_text, reply_markup=start_markup)
