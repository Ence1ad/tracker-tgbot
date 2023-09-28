from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.redis_tracker_commands import is_redis_hexists_tracker
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import start_menu_inline_kb
from tgbot.utils.answer_text import started_tracker_text


async def exit_menu_handler(call: CallbackQuery, state: FSMContext, redis_client: Redis,
                            buttons: AppButtons,  i18n: TranslatorRunner) -> Message:

    """
    The exit_menu_handler function is a callback handler for the exit_menu state.
    It clears the user's FSMContext and returns them to either their main menu with tracker text or
    the main menu without one depending on whether they have an active tracker.

    :param call: CallbackQuery: Get the callback query object from the callback inline button
    :param state: FSMContext: Clear the state of the user
    :param redis_client: Redis: Get the redis client from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the current language of the user from the middleware.
     Translate the buttons and the message text
    :return: A message with the options_text and the start menu buttons
    """
    user_id: int = call.from_user.id
    markup: InlineKeyboardMarkup = await start_menu_inline_kb(await buttons.main_menu_buttons(), i18n)
    await state.clear()
    if await is_redis_hexists_tracker(user_id, redis_client):
        text: str = await started_tracker_text(user_id=user_id, redis_client=redis_client, i18n=i18n,
                                               title='started_tracker_title')
        return await call.message.edit_text(text=text, reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('options_text'), reply_markup=markup)
