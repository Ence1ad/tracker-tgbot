import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler_di import ContextSchedulerDecorator
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import redis_hmset_tracker_data, redis_incr_user_day_trackers, redis_expireat_midnight
from tgbot.schedule.schedule_jobs import delete_tracker_job
from tgbot.utils.answer_text import new_tracker_text, not_enough_data_text
from tgbot.keyboards.callback_factories import ActionCD

from db.tracker.tracker_db_command import create_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.app_buttons import AppButtons


async def create_new_tracker(
        call: CallbackQuery, callback_data: ActionCD, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
        apscheduler: ContextSchedulerDecorator, redis_client: Redis, buttons: AppButtons
) -> Message:
    user_id = call.from_user.id
    action_name = callback_data.action_name
    action_id = callback_data.action_id
    state_data = await state.get_data()
    category_id = state_data['category_id']
    category_name = state_data['category_name']
    try:
        tracker_id = str(await create_tracker(user_id, category_id=category_id, action_id=action_id,
                                              db_session=db_session))
    except IntegrityError as ex:
        logging.exception(ex)
        markup = await menu_inline_kb(await buttons.tracker_menu_start())
        return await call.message.edit_text(text=f"{not_enough_data_text}", reply_markup=markup)
    else:
        await redis_hmset_tracker_data(user_id, tracker_id=tracker_id, action_id=action_id, action_name=action_name,
                                       category_id=category_id, category_name=category_name, redis_client=redis_client)
        await redis_incr_user_day_trackers(user_id, redis_client)
        # Set expire at every midnight for user trackers
        await redis_expireat_midnight(user_id, redis_client)
        # If user not stop the tracker, it will be deleted automatically
        await delete_tracker_job(scheduler=apscheduler, call=call)
        markup = await menu_inline_kb(await buttons.tracker_menu_stop())
        return await call.message.edit_text(text=f"{new_tracker_text} {action_name}", reply_markup=markup)
