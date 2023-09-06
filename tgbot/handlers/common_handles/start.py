from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from cache.redis_commands import redis_started_tracker, is_redis_tracker_exist, redis_create_user, redis_get_user
from db.users.users_commands import create_user
from tgbot.keyboards.buttons_names import start_menu_buttons
from tgbot.keyboards.inline_kb import start_menu_inline_kb
from tgbot.utils.answer_text import user_in_db_text, new_user_text, launch_tracker_text


async def command_start_handler(message: Message, db_session: AsyncSession) -> None:
    """
    Function react to tap on "/start" command. Function check if user exist in db,
    function just return some answer as message, else create user in db and return answer as message.
    :param message: Message
    :param db_session: AsyncSession
    :return: Coroutine[Any]
    """
    user_id: int = message.from_user.id
    await message.delete()
    user_from_cache: bool = await redis_get_user(user_id)
    # Get keyboard
    start_markup = await start_menu_inline_kb(start_menu_buttons)
    # Check if sender already in DB
    if user_from_cache:
        if await is_redis_tracker_exist(user_id):
            started_text = await redis_started_tracker(user_id)
            await message.answer(text=launch_tracker_text + started_text, reply_markup=start_markup)
        else:
            await message.answer(text=user_in_db_text, reply_markup=start_markup)
    else:
        # Add a new user to the cache
        await redis_create_user(user_id)
        # Add a new user to the database
        await create_user(
            user_id=user_id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            db_session=db_session
        )
        await message.answer(text=new_user_text, reply_markup=start_markup)

