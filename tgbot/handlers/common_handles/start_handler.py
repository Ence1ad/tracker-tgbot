from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.trackers_redis_manager import is_redis_hexists_tracker
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.utils.tracker_info import started_tracker_info


async def command_start_handler(
        message: Message, redis_client: Redis, buttons: AppButtons, state: FSMContext,
        i18n: TranslatorRunner
) -> Message:
    """Handle the /start command and display the main menu to the user.

    Note:
    ----
        This function handles the /start command, clears the user's FSM state, and
        displays the main menu.
        It also checks if the user has a started tracker and provides information if
        applicable.

    :param message: Message: The Message object representing the user's message.
    :param redis_client: Redis: The Redis client for data storage.
    :param buttons: AppButtons: An instance of AppButtons for button configuration.
    :param state: FSMContext: The finite state machine (FSM) context for the user.
    :param i18n: TranslatorRunner: An internationalization runner for text localization.
    :return: Message: The response message to be sent to the user.
    """
    user_id: int = message.from_user.id
    await message.delete()
    await state.clear()
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        await buttons.general_btn_source.main_menu_buttons(), i18n, is_cancel=True
    )
    if await is_redis_hexists_tracker(user_id, redis_client):
        tracker_info: str = await started_tracker_info(
            user_id=user_id, redis_client=redis_client, title='started_tracker_title',
            i18n=i18n,
        )
        return await message.answer(text=tracker_info, reply_markup=markup)
    else:
        return await message.answer(text=i18n.get('user_in_db_text'),
                                    reply_markup=markup)
