from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from cache.reports_redis_manager import redis_set_report_need_upd
from cache.trackers_redis_manager import is_redis_hexists_tracker, \
    redis_hget_tracker_data, redis_delete_tracker
from db.operations.tracker_operations import select_tracker_duration
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.tracker_info import started_tracker_info


async def check_is_launched_tracker(
        call: CallbackQuery, redis_client: Redis, buttons: AppButtons,
        i18n: TranslatorRunner
) -> Message:
    """Check if a tracker is launched for the user and provide options to stop it.

    This function checks whether a tracker is currently running for the user.
    If a tracker is running, it offers the user an option to stop it. If no tracker is
    running, it provides options to start a new tracker or manage other settings.

    :param call: CallbackQuery: The CallbackQuery object representing the user's
    interaction.
    :param redis_client: Redis: The Redis client for managing tracker-related data.
    :param buttons: AppButtons: The AppButtons object containing button configurations.
    :param i18n: TranslatorRunner: The TranslatorRunner for handling language
    localization.
    :return: Message: The message to be sent to the user as a response.
    """
    user_id: int = call.from_user.id
    is_tracker: bool = await is_redis_hexists_tracker(user_id, redis_client)
    if is_tracker:
        track_text: str = await started_tracker_info(
            user_id=user_id, redis_client=redis_client, i18n=i18n,
            title='started_tracker_title'
        )
        await call.message.delete()
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.general_btn_source.yes_no_menu(), i18n)
        return await call.message.answer(
            text=track_text + i18n.get('answer_stop_tracker_text'),
            reply_markup=markup)
    else:
        await call.message.delete()
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.trackers_btn_source.tracker_menu_start(),
            i18n)
        return await call.message.answer(text=i18n.get('not_launched_tracker_text'),
                                         reply_markup=markup)


async def stop_tracker_yes_handler(
        call: CallbackQuery, db_session: AsyncSession, redis_client: Redis,
        buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """Handle the user's confirmation to stop a running tracker.

    This function handles the user's confirmation to stop a running tracker.
    It stops the tracker, deletes it from the Redis database, and sets a flag
    indicating that reports need to be updated.

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
    tracker_id: bytes = await redis_hget_tracker_data(user_id, redis_client,
                                                      'tracker_id')
    if tracker_id:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.trackers_btn_source.tracker_menu_start(),
            i18n)
        await select_tracker_duration(user_id=user_id, tracker_id=int(tracker_id),
                                      db_session=db_session)
        track_text: str = await started_tracker_info(
            user_id=user_id, redis_client=redis_client, i18n=i18n,
            title='stop_tracker_text'
        )
        # delete tracker from redis db
        await redis_delete_tracker(user_id, redis_client)
        # Set the flag that reports need to update
        await redis_set_report_need_upd(user_id, redis_client, value=1)
        return await call.message.edit_text(text=track_text, reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.trackers_btn_source.tracker_menu_stop(), i18n)
        return await call.message.edit_text(text=i18n.get('not_launched_tracker_text'),
                                            reply_markup=markup)


async def stop_tracker_no_handler(call: CallbackQuery, buttons: AppButtons,
                                  i18n: TranslatorRunner) -> Message:
    """Handle the user's choice not to stop a running tracker.

    This function handles the user's choice not to stop a running tracker.
    It provides options to continue managing the tracker or return to the main menu.

    :param call: CallbackQuery: The CallbackQuery object representing the user's
    interaction.
    :param buttons: AppButtons: The AppButtons object containing button configurations.
    :param i18n: TranslatorRunner: The TranslatorRunner for handling language
    localization.
    :return: Message: The message to be sent to the user as a response.
    """
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.trackers_btn_source.tracker_menu_stop(), i18n)
    return await call.message.edit_text(text=i18n.get('options_text'),
                                        reply_markup=markup)
