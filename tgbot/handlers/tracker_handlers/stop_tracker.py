from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_commands import redis_delete_tracker, redis_hget_tracker_data
from db.tracker.tracker_db_command import stop_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import tracker_menu_buttons_stop, tracker_menu_buttons_start
from tgbot.utils.answer_text import stop_tracker_text, not_launched_tracker_text, started_tracker_text


async def stop_tracker_handler(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession], redis_client: Redis
                               ) -> Message:
    user_id: int = call.from_user.id
    tracker_id = int(await redis_hget_tracker_data(user_id, redis_client, 'tracker_id'))
    await call.message.delete()
    if tracker_id:
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        await stop_tracker(user_id=user_id, tracker_id=tracker_id, db_session=db_session)
        track_text = await started_tracker_text(user_id, redis_client)
        # delete tracker from redis db
        await redis_delete_tracker(user_id, redis_client)
        return await call.message.answer(text=stop_tracker_text + track_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(tracker_menu_buttons_stop)
        return await call.message.edit_text(text=not_launched_tracker_text, reply_markup=markup)
