from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import is_redis_hexists_tracker, redis_decr_user_day_trackers
from db.tracker.tracker_db_command import select_stopped_trackers, delete_tracker
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.keyboards.callback_factories import TrackerOperation, TrackerCD


async def select_removing_tracker(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession],
                                  redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    user_id = call.from_user.id
    tracker = await select_stopped_trackers(user_id, db_session)
    if tracker:
        markup = await callback_factories_kb(tracker, enum_val=TrackerOperation.DEL)
        return await call.message.edit_text(text=i18n.get('daily_tracker_text'), reply_markup=markup)
    else:
        await call.message.delete()
        markup = await _get_right_tracker_markup(user_id, redis_client, buttons, i18n)
        return await call.message.answer(text=i18n.get('empty_tracker_text'), reply_markup=markup)


async def del_tracking_data(call: CallbackQuery, callback_data: TrackerCD,
                            db_session: async_sessionmaker[AsyncSession], redis_client: Redis,
                            buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    user_id = call.from_user.id
    tracker_id = callback_data.tracker_id
    returning = await delete_tracker(user_id=user_id, tracker_id=tracker_id, db_session=db_session)
    markup = await _get_right_tracker_markup(user_id, redis_client, buttons, i18n)
    if returning:
        await redis_decr_user_day_trackers(user_id, redis_client)
        return await call.message.edit_text(text=i18n.get('delete_tracker_text'), reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('already_delete_tracker_text'), reply_markup=markup)


async def _get_right_tracker_markup(user_id: int, redis_client: Redis,
                                    buttons: AppButtons, i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    is_started_tracker: bool = await is_redis_hexists_tracker(user_id, redis_client)
    start_tracker_menu_buttons = await menu_inline_kb(await buttons.tracker_menu_start(), i18n)
    stop_tracker_menu_buttons = await menu_inline_kb(await buttons.tracker_menu_stop(), i18n)
    if not is_started_tracker:
        return start_tracker_menu_buttons
    else:
        return stop_tracker_menu_buttons
