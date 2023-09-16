from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_commands import is_redis_tracker_exist
from db.tracker.tracker_db_command import select_stopped_trackers, delete_tracker
from tgbot.keyboards.buttons_names import tracker_menu_buttons_start, tracker_menu_buttons_stop
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import daily_tracker_text, empty_tracker_text, delete_tracker_text, \
    already_delete_tracker_text
from tgbot.keyboards.callback_factories import TrackerOperation, TrackerCD


async def select_removing_tracker(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession]
                                  ) -> Message:
    user_id = call.from_user.id
    tracker = await select_stopped_trackers(user_id, db_session)
    if tracker:
        markup = await callback_factories_kb(tracker, enum_val=TrackerOperation.DEL)
        return await call.message.edit_text(text=daily_tracker_text, reply_markup=markup)
    else:
        await call.message.delete()
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        return await call.message.answer(text=empty_tracker_text, reply_markup=markup)


async def del_tracking_data(call: CallbackQuery, callback_data: TrackerCD,
                            db_session: async_sessionmaker[AsyncSession], redis_client: Redis) -> Message:
    user_id = call.from_user.id
    tracker_id = callback_data.tracker_id
    returning = await delete_tracker(user_id=user_id, tracker_id=tracker_id, db_session=db_session)
    markup = await _get_right_tracker_menu_buttons(user_id, redis_client)
    if returning:
        return await call.message.edit_text(text=delete_tracker_text, reply_markup=markup)
    else:
        return await call.message.edit_text(text=already_delete_tracker_text, reply_markup=markup)


async def _get_right_tracker_menu_buttons(user_id: int, redis_client: Redis) -> InlineKeyboardMarkup:
    is_started_tracker: bool = await is_redis_tracker_exist(user_id, redis_client)
    start_tracker_menu_buttons = await menu_inline_kb(tracker_menu_buttons_start)
    stop_tracker_menu_buttons = await menu_inline_kb(tracker_menu_buttons_stop)
    if not is_started_tracker:
        return start_tracker_menu_buttons
    else:
        return stop_tracker_menu_buttons
