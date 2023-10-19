from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.trackers_redis_manager import is_redis_hexists_tracker
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.tracker_info import started_tracker_info


async def trackers_main_menu_handler(call: CallbackQuery, redis_client: Redis,
                                     buttons: AppButtons,
                                     i18n: TranslatorRunner) -> Message:
    """Handle the main menu for trackers.

    This function handles the main menu for tracker-related operations, allowing users
    to start, stop, or manage trackers.

    If a tracker is already started, it displays information about the started tracker
    and provides options to stop it.
    If no tracker is running, it offers options to start a new tracker or manage other
    settings.
    :param call: CallbackQuery: The CallbackQuery object representing the user's
    interaction.
    :param redis_client: Redis: The Redis client for managing tracker-related data.
    :param buttons: AppButtons: The AppButtons object containing button configurations.
    :param i18n: TranslatorRunner: The TranslatorRunner for handling language
    localization.
    :return: Message: The message to be sent to the user as a response.
    """
    user_id: int = call.from_user.id
    await call.message.delete()
    if await is_redis_hexists_tracker(user_id, redis_client):
        started_tracker: str = await started_tracker_info(
            user_id=user_id, redis_client=redis_client, i18n=i18n,
            title='started_tracker_title'
        )
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.trackers_btn_source.tracker_menu_stop(), i18n
        )
        return await call.message.answer(text=started_tracker, reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            await buttons.trackers_btn_source.tracker_menu_start(), i18n
        )
        return await call.message.answer(text=i18n.get('options_text'),
                                         reply_markup=markup)
