from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.trackers_redis_manager import is_redis_hexists_tracker
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.utils.answer_text import started_tracker_text
from tgbot.keyboards.inline_kb import menu_inline_kb


async def trackers_main_menu_handler(call: CallbackQuery, redis_client: Redis, buttons: AppButtons,
                                     i18n: TranslatorRunner) -> Message:
    """
    The trackers_main_menu_handler function checks if there is an active tracker in Redis
    and returns the appropriate message with buttons.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param redis_client: Redis: Get the redis client from the middleware.
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: The message text and the inline keyboard with tracker menu buttons
    """
    user_id: int = call.from_user.id
    await call.message.delete()
    if await is_redis_hexists_tracker(user_id, redis_client):
        started_tracker: str = await started_tracker_text(user_id=user_id, redis_client=redis_client, i18n=i18n,
                                                          title='started_tracker_title')
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.trackers_btn_source.tracker_menu_stop(),
                                                            i18n)
        return await call.message.answer(text=started_tracker, reply_markup=markup)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(await buttons.trackers_btn_source.tracker_menu_start(),
                                                            i18n)
        return await call.message.answer(text=i18n.get('options_text'), reply_markup=markup)
