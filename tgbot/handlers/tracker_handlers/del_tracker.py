from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from db.tracker.tracker_db_command import select_stopped_trackers, delete_tracker
from tgbot.keyboards.buttons_names import tracker_menu_buttons_start
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import daily_tracker_text, empty_tracker_text, delete_tracker_text, \
    already_delete_tracker_text
from tgbot.keyboards.callback_factories import TrackerOperation, TrackerCD


async def select_removing_tracker(call: CallbackQuery, db_session: AsyncSession):
    user_id = call.from_user.id
    tracker = await select_stopped_trackers(user_id, db_session)
    tracker = tracker
    if tracker:
        # await call.message.delete()
        markup = await callback_factories_kb(tracker, enum_val=TrackerOperation.DEL)
        await call.message.edit_text(text=daily_tracker_text, reply_markup=markup)
    else:
        await call.message.delete()
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        await call.message.answer(text=empty_tracker_text, reply_markup=markup)


async def del_tracking_data(call: CallbackQuery, callback_data: TrackerCD, db_session: AsyncSession):
    user_id = call.from_user.id
    tracker_id = callback_data.tracker_id
    returning = await delete_tracker(user_id=user_id, tracker_id=tracker_id, db_session=db_session)
    if returning:
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        await call.message.edit_text(text=delete_tracker_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        await call.message.edit_text(text=already_delete_tracker_text, reply_markup=markup)
