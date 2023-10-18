from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.trackers_redis_manager import is_redis_hexists_tracker
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.tracker_info import started_tracker_info


async def exit_menu_handler(call: CallbackQuery, state: FSMContext, redis_client: Redis,
                            buttons: AppButtons,  i18n: TranslatorRunner) -> Message:
    """Handle the user's request to exit the current menu or operation.

    :param call: CallbackQuery: The CallbackQuery object representing the user's
    request.
    :param state: FSMContext: The finite state machine (FSM) context for the user.
    :param redis_client: Redis: The Redis client for data storage.
    :param buttons: AppButtons: An instance of AppButtons for accessing application
     buttons.
    :param i18n: TranslatorRunner: An internationalization runner for text localization.
    :return: Message: A response message indicating the exit from the current menu or
    operation.
    """
    user_id: int = call.from_user.id
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.general_btn_source.main_menu_buttons(), i18n, is_cancel=True
    )
    await state.clear()
    if await is_redis_hexists_tracker(user_id, redis_client):
        text: str = await started_tracker_info(
            user_id=user_id, redis_client=redis_client, i18n=i18n,
            title='started_tracker_title'
        )
        return await call.message.edit_text(text=text, reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('options_text'),
                                            reply_markup=markup)
