from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from cache.reports_redis_manager import redis_set_report_need_upd
from cache.trackers_redis_manager import is_redis_hexists_tracker, redis_hget_tracker_data, redis_delete_tracker
from db.operations.tracker_operations import select_tracker_duration
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.utils.answer_text import started_tracker_text


async def check_is_launched_tracker(call: CallbackQuery, redis_client: Redis, buttons: AppButtons,
                                    i18n: TranslatorRunner) -> Message:
    """
    The check_is_launched_tracker function checks if the user has launched a tracker.
    If the user has launched a tracker, then it displays information about this tracker and offers to stop it.
    Otherwise, it displays an offer to launch a new one.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param redis_client: Redis: Get the redis client from the middleware.
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with the text and menu buttons
    """
    user_id: int = call.from_user.id
    is_tracker: bool = await is_redis_hexists_tracker(user_id, redis_client)
    if is_tracker:
        track_text: str = await started_tracker_text(user_id=user_id, redis_client=redis_client, i18n=i18n,
                                                     title='started_tracker_title')
        await call.message.delete()
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.general_btn_source.yes_no_menu(), i18n)
        return await call.message.answer(text=track_text + i18n.get('answer_stop_tracker_text'),
                                         reply_markup=markup)
    else:
        await call.message.delete()
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.trackers_btn_source.tracker_menu_start(),
                                                            i18n)
        return await call.message.answer(text=i18n.get('not_launched_tracker_text'), reply_markup=markup)


async def stop_tracker_yes_handler(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession],
                                   redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    """
    The stop_tracker_yes_handler function is called when the user clicks on the &quot;Yes&quot; button in a message
    asking if they want to stop their tracker. If there is an active tracker, it will be stopped, updated
    the track_end and duration fields in trackers db table and deleted from the Redis database.
    The user will then be returned to the main menu.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param redis_client: Redis: Get the redis client from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: The message text and the inline keyboard with the menu buttons
    """
    user_id: int = call.from_user.id
    tracker_id: bytes = await redis_hget_tracker_data(user_id, redis_client, 'tracker_id')
    if tracker_id:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.trackers_btn_source.tracker_menu_start(),
                                                            i18n)
        await select_tracker_duration(user_id=user_id, tracker_id=int(tracker_id), db_session=db_session)
        track_text: str = await started_tracker_text(user_id=user_id, redis_client=redis_client, i18n=i18n,
                                                     title='stop_tracker_text')
        # delete tracker from redis db
        await redis_delete_tracker(user_id, redis_client)
        # Set the flag that reports need to update
        await redis_set_report_need_upd(user_id, redis_client, value=1)
        return await call.message.edit_text(text=track_text, reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.trackers_btn_source.tracker_menu_stop(), i18n)
        return await call.message.edit_text(text=i18n.get('not_launched_tracker_text'), reply_markup=markup)


async def stop_tracker_no_handler(call: CallbackQuery, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    """
    The stop_tracker_no_handler function will display an error message to the user,
    and then return them to the main menu.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: The message text and the inline keyboard with the menu buttons
    """
    markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.trackers_btn_source.tracker_menu_stop(), i18n)
    return await call.message.edit_text(text=i18n.get('options_text'), reply_markup=markup)
