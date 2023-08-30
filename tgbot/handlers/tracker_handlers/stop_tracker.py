from datetime import datetime, timedelta

from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from cache.redis_commands import redis_hget_start_time, redis_delete_tracker, tracker_text
from db.tracker.tracker_db_command import update_tracker, select_started_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import tracker_menu_buttons_stop, tracker_menu_buttons_start
from tgbot.utils.answer_text import stop_tracker_text, not_launched_tracker_text


async def stop_tracker_handler(call: CallbackQuery, db_session: AsyncSession):
    user_id: int = call.from_user.id
    start_datetime: datetime = await redis_hget_start_time(user_id)
    delta: timedelta = datetime.now() - start_datetime
    end_datetime: datetime = (start_datetime + delta).replace(microsecond=0)
    # print(call_datetime, type(call_datetime))
    tracker = await select_started_tracker(user_id, db_session)
    await call.message.delete()
    if tracker:
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        tracker_id = tracker[0].tracker_id
        await update_tracker(user_id=user_id, call_datetime=end_datetime, tracker_id=tracker_id, db_session=db_session)
        track_text = await tracker_text(user_id)
        # delete tracker from redis db
        await redis_delete_tracker(user_id)
        await call.message.answer(text=stop_tracker_text + track_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(tracker_menu_buttons_stop)
        await call.message.edit_text(text=not_launched_tracker_text, reply_markup=markup)
