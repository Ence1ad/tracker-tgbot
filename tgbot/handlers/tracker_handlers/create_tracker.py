from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler_di import ContextSchedulerDecorator
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import redis_hmset_create_tracker, redis_incr_user_day_trackers, \
    redis_expireat_midnight, is_redis_hexists_tracker, redis_get_user_day_trackers
from config import settings
from db.actions.actions_db_commands import select_category_actions
from tgbot.handlers.categories_handlers.read_categories import get_categories
from tgbot.schedule.schedule_jobs import delete_tracker_job
from tgbot.keyboards.callback_factories import ActionCD, CategoryCD, ActionOperation

from db.tracker.tracker_db_command import create_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.utils.states import TrackerState


async def pass_tracker_checks(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession], redis_client: Redis,
                              buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    user_id = call.from_user.id
    user_trackers_cnt = await redis_get_user_day_trackers(user_id, redis_client)
    if user_trackers_cnt is None or (int(user_trackers_cnt) < settings.USER_TRACKERS_DAILY_LIMIT):
        return await get_categories(call=call, db_session=db_session, buttons=buttons, i18n=i18n)
    else:
        markup = await menu_inline_kb(await buttons.tracker_menu_start(), i18n)
        await call.message.delete()
        return await call.message.answer(text=i18n.get('tracker_daily_limit_text'), reply_markup=markup)


async def take_action_4_tracker(call: CallbackQuery, callback_data: CategoryCD, state: FSMContext, buttons: AppButtons,
                                db_session: async_sessionmaker[AsyncSession], i18n: TranslatorRunner) -> Message:
    user_id = call.from_user.id
    category_id = callback_data.category_id
    category_name = callback_data.category_name
    await state.update_data(category_id=category_id, category_name=category_name)
    actions = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    if actions:
        await state.set_state(TrackerState.WAIT_CATEGORY_DATA)
        markup = await callback_factories_kb(actions, ActionOperation.READ_TRACKER)
        return await call.message.edit_text(
            text=i18n.get('select_category_4_tracker', category_name=category_name, new_line='\n'), reply_markup=markup)
    else:
        await state.clear()
        markup = await menu_inline_kb(await buttons.main_menu_buttons(), i18n)
        return await call.message.edit_text(text=i18n.get('valid_data_text'), reply_markup=markup)


async def create_new_tracker(
        call: CallbackQuery, callback_data: ActionCD, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
        apscheduler: ContextSchedulerDecorator, redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    user_id = call.from_user.id
    action_name = callback_data.action_name
    action_id = callback_data.action_id
    state_data = await state.get_data()
    category_id = state_data['category_id']
    category_name = state_data['category_name']
    await state.clear()
    if not await is_redis_hexists_tracker(user_id, redis_client):
        tracker_id = str(await create_tracker(user_id, category_id=category_id, action_id=action_id,
                                              db_session=db_session))
        await redis_hmset_create_tracker(
            user_id, tracker_id=tracker_id, action_id=action_id, action_name=action_name,
            category_id=category_id, category_name=category_name, redis_client=redis_client
        )
        await redis_incr_user_day_trackers(user_id, redis_client)
        # Set expire at every midnight for user trackers
        await redis_expireat_midnight(user_id, redis_client)
        # If user not stop the tracker, it will be deleted automatically
        await _setup_duration_schedule_checker(scheduler=apscheduler, user_id=user_id, i18n=i18n)
        markup = await menu_inline_kb(await buttons.tracker_menu_stop(), i18n)
        return await call.message.edit_text(text=i18n.get('new_tracker_text', action_name=action_name),
                                            reply_markup=markup)
    else:
        markup = await menu_inline_kb(await buttons.tracker_menu_start(), i18n)
        return await call.message.edit_text(text=i18n.get('not_enough_data_text'), reply_markup=markup)


async def _setup_duration_schedule_checker(scheduler: ContextSchedulerDecorator, user_id: int,
                                           i18n: TranslatorRunner) -> None:
    msg_text = i18n.get("too_long_tracker")
    await delete_tracker_job(scheduler=scheduler, user_id=user_id, msg_text=msg_text)
