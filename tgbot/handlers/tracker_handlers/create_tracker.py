from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from apscheduler.job import Job
from apscheduler_di import ContextSchedulerDecorator
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from cache.trackers_redis_manager import redis_hmset_create_tracker, \
    redis_incr_user_day_trackers, redis_expireat_midnight, is_redis_hexists_tracker, \
    redis_get_user_day_trackers
from config import settings
from db.operations.actions_operations import select_category_actions
from db.operations.tracker_operations import create_tracker
from tgbot.handlers.categories_handlers.read_categories import \
    categories_main_menu_handler
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import ActionCD, CategoryCD, ActionOperation
from tgbot.keyboards.inline_kb import menu_inline_kb, callback_factories_kb
from tgbot.schedule.schedule_jobs import delete_tracker_job
from tgbot.utils.states import TrackerState


async def pass_tracker_checks(
        call: CallbackQuery, db_session: AsyncSession, redis_client: Redis,
        buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """Check if the user can create a new tracker and provide options accordingly.

    This function checks if the user has exceeded the daily limit for creating trackers.
    If the limit is not exceeded,it allows the user to select categories to create
    trackers for. If the limit is reached, it informs the user about the daily limit.

    :param call:CallbackQuery: The CallbackQuery object representing the user's
    interaction.
    :param db_session: AsyncSession: The database session for querying and updating
    tracker data.
    :param redis_client: Redis: The Redis client for managing tracker-related data.
    :param buttons: AppButtons: The AppButtons object containing button configurations.
    :param i18n: TranslatorRunner: The TranslatorRunner for handling language
     localization.
    :return: Message: The message to be sent to the user as a response.
    """
    user_id: int = call.from_user.id
    user_trackers_cnt: bytes = await redis_get_user_day_trackers(user_id, redis_client)
    if user_trackers_cnt is None or (
            int(user_trackers_cnt) < settings.USER_TRACKERS_DAILY_LIMIT):
        return await categories_main_menu_handler(call=call, db_session=db_session,
                                                  buttons=buttons, i18n=i18n)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.trackers_btn_source.tracker_menu_start(), i18n
        )
        await call.message.delete()
        return await call.message.answer(text=i18n.get('tracker_daily_limit_text'),
                                         reply_markup=markup)


async def take_action_4_tracker(
        call: CallbackQuery, callback_data: CategoryCD, state: FSMContext,
        buttons: AppButtons, db_session: AsyncSession, i18n: TranslatorRunner
) -> Message:
    """Handle the user's selection of an action for creating a new tracker.

    This function handles the user's selection of an action for creating a new tracker.
    It allows the user to choose from available actions and sets the category and
    action details in the tracker state.

    :param call: CallbackQuery: The CallbackQuery object representing the user's
    interaction.
    :param callback_data: CategoryCD: The callback data containing category and action
     information.
    :param state: FSMContext: The finite state machine context for managing user state.
    :param buttons: AppButtons: The AppButtons object containing button configurations.
    :param db_session: AsyncSession: The database session for querying and updating
    tracker data.
    :param i18n: TranslatorRunner: The TranslatorRunner for handling language
    localization.
    :return: Message: The message to be sent to the user as a response.
    """
    user_id: int = call.from_user.id
    category_id: int = callback_data.category_id
    category_name: str = callback_data.category_name
    await state.update_data(category_id=category_id, category_name=category_name)
    actions: Sequence = await select_category_actions(user_id, category_id=category_id,
                                                      db_session=db_session)
    if actions:
        await state.set_state(TrackerState.WAIT_CATEGORY_DATA)
        markup: InlineKeyboardMarkup = await callback_factories_kb(
            actions, ActionOperation.READ_TRACKER
        )
        return await call.message.edit_text(
            text=i18n.get('select_category_4_tracker', category_name=category_name,
                          new_line='\n'), reply_markup=markup)
    else:
        await state.clear()
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.general_btn_source.main_menu_buttons(), i18n)
        return await call.message.edit_text(text=i18n.get('valid_data_text'),
                                            reply_markup=markup)


async def create_new_tracker(
        call: CallbackQuery, callback_data: ActionCD, state: FSMContext,
        db_session: AsyncSession,
        apscheduler: ContextSchedulerDecorator, redis_client: Redis,
        buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """Create a new tracker based on user selection.

    This function creates a new tracker based on the user's selection of category and
    action. It checks if a tracker is already running for the user and if not,
    creates a new tracker, updates Redis data, and sets up a schedule job to
    automatically delete the tracker if not stopped.

    Returns:
        Message: The message to be sent to the user as a response.
    :param call: CallbackQuery: The CallbackQuery object representing the user's
    interaction.
    :param callback_data: ActionCD: The callback data containing action information.
    :param state: FSMContext: The finite state machine context for managing user state.
    :param db_session: AsyncSession: The database session for querying and updating
    tracker data.
    :param apscheduler: ContextSchedulerDecorator: The APScheduler context decorator for
     scheduling jobs.
    :param redis_client: Redis: The Redis client for managing tracker-related data.
    :param buttons: AppButtons: The AppButtons object containing button configurations.
    :param i18n: TranslatorRunner: The TranslatorRunner for handling language
     localization.
    :return:
    """
    user_id: int = call.from_user.id
    action_name: str = callback_data.action_name
    action_id: int = callback_data.action_id
    state_data: dict = await state.get_data()
    category_id: int = state_data['category_id']
    category_name: str = state_data['category_name']
    await state.clear()
    if not await is_redis_hexists_tracker(user_id, redis_client):
        tracker_id: str = str(
            await create_tracker(user_id, category_id=category_id, action_id=action_id,
                                 db_session=db_session))
        await redis_hmset_create_tracker(
            user_id, tracker_id=tracker_id, action_id=action_id,
            action_name=action_name, category_id=category_id,
            category_name=category_name, redis_client=redis_client
        )
        await redis_incr_user_day_trackers(user_id, redis_client)
        # Set expire at every midnight for user trackers
        await redis_expireat_midnight(user_id, redis_client)
        # If user not stop the tracker, it will be deleted automatically
        await _setup_duration_schedule_checker(scheduler=apscheduler, user_id=user_id,
                                               i18n=i18n)
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.trackers_btn_source.tracker_menu_stop(), i18n)
        return await call.message.edit_text(
            text=i18n.get('new_tracker_text', action_name=action_name),
            reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.trackers_btn_source.tracker_menu_start(),
            i18n)
        return await call.message.edit_text(text=i18n.get('not_enough_data_text'),
                                            reply_markup=markup)


async def _setup_duration_schedule_checker(
        scheduler: ContextSchedulerDecorator, user_id: int, i18n: TranslatorRunner
) -> Job:
    """Set up a scheduled job to check and delete long-running trackers.

    This function sets up a scheduled job using APScheduler to periodically check and
    delete trackers that have been running for an extended period. It helps prevent the
    accumulation of long-running trackers.

    :param scheduler: ContextSchedulerDecorator: The APScheduler context decorator for
    scheduling jobs.
    :param user_id: int: The user's ID for identifying the user.
    :param i18n: TranslatorRunner: The TranslatorRunner for handling language
    localization.
    :return: Job: The scheduled job for tracking and deleting long-running trackers.
    """
    msg_text = i18n.get("too_long_tracker")
    return await delete_tracker_job(scheduler=scheduler, user_id=user_id,
                                    msg_text=msg_text)
