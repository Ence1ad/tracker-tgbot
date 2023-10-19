from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from cache.reports_redis_manager import redis_set_report_need_upd
from cache.trackers_redis_manager import is_redis_hexists_tracker, \
    redis_decr_user_day_trackers
from db.operations.tracker_operations import select_stopped_trackers, delete_tracker
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import TrackerOperation, TrackerCD
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb


async def take_traker_4_delete(
        call: CallbackQuery, db_session: AsyncSession, redis_client: Redis,
        buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """Handle the user's selection of a tracker for deletion.

    This function handles the user's selection of a tracker for deletion. It retrieves
    a list of stopped trackers for the user and allows the user to choose a tracker to
    delete. If no stopped trackers are available, it provides appropriate feedback.

    :param call: CallbackQuery: The CallbackQuery object representing the user's
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
    stopped_trackers: Sequence = await select_stopped_trackers(user_id, db_session)
    if stopped_trackers:
        markup: InlineKeyboardMarkup = await callback_factories_kb(
            stopped_trackers, enum_val=TrackerOperation.DEL
        )
        return await call.message.edit_text(text=i18n.get('daily_tracker_text'),
                                            reply_markup=markup)
    else:
        await call.message.delete()
        markup: InlineKeyboardMarkup = await _get_right_tracker_markup(user_id,
                                                                       redis_client,
                                                                       buttons, i18n)
        return await call.message.answer(text=i18n.get('empty_stopped_tracker_text'),
                                         reply_markup=markup)


async def delete_tracker_handler(
        call: CallbackQuery, callback_data: TrackerCD, db_session: AsyncSession,
        redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """Handle the user's request to delete a specific tracker.

    This function handles the user's request to delete a specific tracker based on the
    user's selection. It deletes the selected tracker from the database and Redis,
    updates daily tracker counts, and notifies the user about the successful deletion
    or the tracker's non-existence.

    :param call: CallbackQuery: The CallbackQuery object representing the user's
    interaction.
    :param callback_data: TrackerCD: The callback data containing tracker information.
    :param db_session: AsyncSession: The database session for querying and updating
    tracker data.
    :param redis_client: Redis: The Redis client for managing tracker-related data.
    :param buttons: AppButtons: The AppButtons object containing button configurations.
    :param i18n: TranslatorRunner: The TranslatorRunner for handling language
    localization.
    :return: Message: The message to be sent to the user as a response.
    """
    user_id: int = call.from_user.id
    tracker_id: int = callback_data.tracker_id
    markup: InlineKeyboardMarkup = await _get_right_tracker_markup(user_id,
                                                                   redis_client,
                                                                   buttons, i18n)
    returning: int = await delete_tracker(user_id=user_id, tracker_id=tracker_id,
                                          db_session=db_session)
    if returning:
        await redis_decr_user_day_trackers(user_id, redis_client)
        await redis_set_report_need_upd(user_id=user_id, redis_client=redis_client,
                                        value=1)
        return await call.message.edit_text(text=i18n.get('delete_tracker_text'),
                                            reply_markup=markup)
    else:
        return await call.message.edit_text(
            text=i18n.get('already_delete_tracker_text'), reply_markup=markup)


async def _get_right_tracker_markup(
        user_id: int, redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner
) -> InlineKeyboardMarkup:
    """Get the appropriate inline keyboard markup for starting or stopping a tracker.

    This function determines whether the user has a currently started tracker and
    provides the corresponding inline keyboard markup for either starting or stopping
    a tracker. If a tracker is running, it offers the option to stop the tracker.
    If no tracker is running, it allows the user to start a tracker.

    :param user_id: int: The user's ID for identifying the user.
    :param redis_client: Redis: The Redis client for managing tracker-related data.
    :param buttons: AppButtons: The AppButtons object containing button configurations.
    :param i18n: TranslatorRunner: The TranslatorRunner for handling language
     localization.
    :return: InlineKeyboardMarkup: The inline keyboard markup for starting or stopping
     a tracker.
    """
    is_started_tracker: bool = await is_redis_hexists_tracker(user_id, redis_client)
    if not is_started_tracker:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.trackers_btn_source.tracker_menu_start(), i18n
        )
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.trackers_btn_source.tracker_menu_stop(), i18n
        )
    return markup
