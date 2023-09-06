import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cache.redis_commands import redis_hmset_tracker_data
from tgbot.utils.answer_text import new_tracker_text, not_enough_data_text
from tgbot.keyboards.callback_factories import ActionCD

from db.tracker.tracker_db_command import create_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.buttons_names import tracker_menu_buttons_stop, tracker_menu_buttons_start


# TODO трекер должен автоматом останавливаться через нужное время
async def create_new_tracker(call: CallbackQuery, callback_data: ActionCD, state: FSMContext, db_session: AsyncSession):
    user_id = call.from_user.id
    # start_time = call.message.date
    action_name = callback_data.action_name
    action_id = callback_data.action_id
    state_data = await state.get_data()
    category_id = state_data['category_id']
    category_name = state_data['category_name']
    try:
        tracker_id = str(await create_tracker(user_id,
                                              category_id=category_id,
                                              action_id=action_id,
                                              db_session=db_session))
        await redis_hmset_tracker_data(user_id,
                                       tracker_id=tracker_id,
                                       action_id=action_id, action_name=action_name,
                                       category_id=category_id, category_name=category_name)
        markup = await menu_inline_kb(tracker_menu_buttons_stop)
        await call.message.edit_text(text=f"{new_tracker_text} {action_name}", reply_markup=markup)
    except IntegrityError as ex:
        logging.exception(ex)
        markup = await menu_inline_kb(tracker_menu_buttons_start)
        await call.message.edit_text(text=f"{not_enough_data_text}", reply_markup=markup)
