from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from apscheduler.job import Job
from apscheduler_di import ContextSchedulerDecorator
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import redis_hmset_create_tracker, redis_incr_user_day_trackers, \
    redis_expireat_midnight, is_redis_hexists_tracker, redis_get_user_day_trackers
from config import settings
from db.actions.actions_db_commands import select_category_actions
from db.tracker.tracker_db_command import create_tracker
from tgbot.handlers.categories_handlers.read_categories import categories_main_menu_handler
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import ActionCD, CategoryCD, ActionOperation
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb
from tgbot.schedule.schedule_jobs import delete_tracker_job
from tgbot.utils.states import TrackerState


async def pass_tracker_checks(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession], redis_client: Redis,
                              buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    """
    The pass_tracker_checks function is a helper function that checks if the user has reached their daily limit
    of trackers. If they have, it will return an error message to the user and delete the previous message.
    If not, it will call the categories_main_menu_handler function.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param redis_client: Redis: Get the redis client from the middleware. Get the user's trackers count from redis
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :return: The categories_main_menu_handler function
    """
    user_id: int = call.from_user.id
    user_trackers_cnt: bytes = await redis_get_user_day_trackers(user_id, redis_client)
    if user_trackers_cnt is None or (int(user_trackers_cnt) < settings.USER_TRACKERS_DAILY_LIMIT):
        return await categories_main_menu_handler(call=call, db_session=db_session, buttons=buttons, i18n=i18n)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.tracker_menu_start(), i18n)
        await call.message.delete()
        return await call.message.answer(text=i18n.get('tracker_daily_limit_text'), reply_markup=markup)


async def take_action_4_tracker(call: CallbackQuery, callback_data: CategoryCD, state: FSMContext, buttons: AppButtons,
                                db_session: async_sessionmaker[AsyncSession], i18n: TranslatorRunner) -> Message:
    """
    The take_action_4_tracker function is used to select the action for tracker.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param callback_data: CategoryCD: Get the category id and name from the callback data
    :param state: FSMContext: Store the state of the user in a conversation
    :param buttons: AppButtons: Get the buttons from the middleware
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware.
     Translate the buttons and the message text
    :return: A list of actions for the selected category
    """
    user_id: int = call.from_user.id
    category_id: int = callback_data.category_id
    category_name: str = callback_data.category_name
    await state.update_data(category_id=category_id, category_name=category_name)
    actions: list[Row] = await select_category_actions(user_id, category_id=category_id, db_session=db_session)
    if actions:
        await state.set_state(TrackerState.WAIT_CATEGORY_DATA)
        markup: InlineKeyboardMarkup = await callback_factories_kb(actions, ActionOperation.READ_TRACKER)
        return await call.message.edit_text(
            text=i18n.get('select_category_4_tracker', category_name=category_name, new_line='\n'), reply_markup=markup)
    else:
        await state.clear()
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.main_menu_buttons(), i18n)
        return await call.message.edit_text(text=i18n.get('valid_data_text'), reply_markup=markup)


async def create_new_tracker(
        call: CallbackQuery, callback_data: ActionCD, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
        apscheduler: ContextSchedulerDecorator, redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """
    The create_new_tracker function is used to create a new tracker for the user.
        It will check if there is already an active tracker, and if not it will create one.
        If there is an active tracker, it will return a message saying that the user needs to stop their current
        action before starting another one.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param callback_data: ActionCD: Get the action_id and action_name
    :param state: FSMContext: Store the state of the user
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param apscheduler: ContextSchedulerDecorator: Schedule the job
    :param redis_client: Redis:  Get the redis client from the middleware.
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: The message with the text &quot;new tracker created&quot;
    """
    user_id: int = call.from_user.id
    action_name: str = callback_data.action_name
    action_id: int = callback_data.action_id
    state_data: dict = await state.get_data()
    category_id: int = state_data['category_id']
    category_name: str = state_data['category_name']
    await state.clear()
    if not await is_redis_hexists_tracker(user_id, redis_client):
        tracker_id: str = str(await create_tracker(user_id, category_id=category_id, action_id=action_id,
                              db_session=db_session))  # Create a new tracker in the database
        await redis_hmset_create_tracker(user_id, tracker_id=tracker_id, action_id=action_id, action_name=action_name,
                                         category_id=category_id, category_name=category_name,
                                         redis_client=redis_client)
        await redis_incr_user_day_trackers(user_id, redis_client)
        # Set expire at every midnight for user trackers
        await redis_expireat_midnight(user_id, redis_client)
        # If user not stop the tracker, it will be deleted automatically
        await _setup_duration_schedule_checker(scheduler=apscheduler, user_id=user_id, i18n=i18n)
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.tracker_menu_stop(), i18n)
        return await call.message.edit_text(text=i18n.get('new_tracker_text', action_name=action_name),
                                            reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.tracker_menu_start(), i18n)
        return await call.message.edit_text(text=i18n.get('not_enough_data_text'), reply_markup=markup)


async def _setup_duration_schedule_checker(scheduler: ContextSchedulerDecorator, user_id: int,
                                           i18n: TranslatorRunner) -> Job:
    msg_text = i18n.get("too_long_tracker")
    return await delete_tracker_job(scheduler=scheduler, user_id=user_id, msg_text=msg_text)
