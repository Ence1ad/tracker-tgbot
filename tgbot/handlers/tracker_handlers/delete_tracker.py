from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import is_redis_hexists_tracker, redis_decr_user_day_trackers
from db.tracker.tracker_db_command import select_stopped_trackers, delete_tracker
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.keyboards.callback_factories import TrackerOperation, TrackerCD


async def take_traker_4_delete(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession],
                               redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    user_id: int = call.from_user.id
    stopped_trackers: list[Row] = await select_stopped_trackers(user_id, db_session)
    if stopped_trackers:
        markup: InlineKeyboardMarkup = await callback_factories_kb(stopped_trackers, enum_val=TrackerOperation.DEL)
        return await call.message.edit_text(text=i18n.get('daily_tracker_text'), reply_markup=markup)
    else:
        await call.message.delete()
        markup: InlineKeyboardMarkup = await _get_right_tracker_markup(user_id, redis_client, buttons, i18n)
        return await call.message.answer(text=i18n.get('empty_stopped_tracker_text'), reply_markup=markup)


async def delete_tracker_handler(
        call: CallbackQuery, callback_data: TrackerCD, db_session: async_sessionmaker[AsyncSession],
        redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner
) -> Message:
    """
    The delete_tracker_handler function is responsible for deleting a tracker from the database.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param callback_data: TrackerCD: Get the tracker_id from the callback data
    :param db_session: async_sessionmaker[AsyncSession]: Get the database session from the middleware
    :param redis_client: Redis: Get the user's trackers from redis
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return:  A message with the text and right menu buttons
    """
    user_id: int = call.from_user.id
    tracker_id: int = callback_data.tracker_id
    markup: InlineKeyboardMarkup = await _get_right_tracker_markup(user_id, redis_client, buttons, i18n)
    returning: int = await delete_tracker(user_id=user_id, tracker_id=tracker_id, db_session=db_session)
    if returning:
        await redis_decr_user_day_trackers(user_id, redis_client)
        return await call.message.edit_text(text=i18n.get('delete_tracker_text'), reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('already_delete_tracker_text'), reply_markup=markup)


async def _get_right_tracker_markup(user_id: int, redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner
                                    ) -> InlineKeyboardMarkup:
    """
    The _get_right_tracker_markup function is a helper function that returns the right InlineKeyboardMarkup
    for the tracker menu. If the user has not started tracking, it will return an InlineKeyboardMarkup with
    the start button. Otherwise, it will return an InlineKeyboardMarkup with a stop button.

    :param user_id: int: Identify the user
    :param redis_client: Redis: Get the redis client from the middleware.
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: The right tracker markup
    """
    is_started_tracker: bool = await is_redis_hexists_tracker(user_id, redis_client)
    if not is_started_tracker:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.tracker_menu_start(), i18n)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.tracker_menu_stop(), i18n)
    return markup
