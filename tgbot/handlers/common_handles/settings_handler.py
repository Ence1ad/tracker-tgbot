from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.redis_language_commands import redis_hget_lang, redis_hset_lang
from config import settings
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb


async def command_settings_handler(message: Message, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    """
    Handle the /settings command.

    It deletes the message sent by the user and sends back the message and inline keyboard with all
    the settings options available to them.

    :param message: Message: Get the message object that was sent by the user
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware
    :return: The message text and the inline keyboard with settings menu buttons

    """
    markup: InlineKeyboardMarkup = await menu_inline_kb(buttons=await buttons.settings_btn_source.settings_menu(),
                                                        i18n=i18n)
    await message.delete()
    return await message.answer(text=i18n.get('options_text'), reply_markup=markup)


async def language_settings(call: CallbackQuery, buttons: AppButtons, i18n: TranslatorRunner, redis_client: Redis
                            ) -> Message:
    """
    The language_settings function is used to change the language of the bot.
    It takes in a CallbackQuery object, an AppButtons object, a TranslatorRunner object and a Redis client.
    The function returns a Message object.

    :param call: CallbackQuery: Get the callback query object from a callback inline button
    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware
    :param redis_client: Redis: Get the redis client from the middleware
    :return: The message text and the inline keyboard with language settings menu
    """
    user_id: int = call.from_user.id
    local: str = await redis_hget_lang(user_id, redis_client=redis_client)
    markup: InlineKeyboardMarkup = await _get_right_markup(buttons=buttons, i18n=i18n, local=local)
    return await call.message.edit_text(text=i18n.get('select_lang_text'), reply_markup=markup)


async def set_user_lang(call: CallbackQuery, redis_client: Redis, i18n: TranslatorRunner,
                        buttons: AppButtons) -> bool:
    """
    The set_user_lang function is a callback handler for the language selection buttons.
    It sets the user's preferred language in Redis and deletes the message with buttons.


    :param call: CallbackQuery: Get the callback query object from a callback inline button
    :param redis_client: Redis: Get the redis client from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware
    :param buttons: AppButtons: Get the buttons from the middleware
    :return: A boolean value
    """
    user_id: int = call.from_user.id
    before_lang_code = await redis_hget_lang(user_id, redis_client=redis_client)
    lang_code: str = _get_language(call_data=call.data, buttons=buttons)
    await redis_hset_lang(user_id, lang_code=lang_code, redis_client=redis_client)
    if before_lang_code != lang_code:
        is_answer: bool = await call.answer(text=i18n.get('set_lang_text'), show_alert=True)
    else:
        is_answer: bool = await call.answer(text=i18n.get('settings_not_change_text'), show_alert=True)
    await call.message.delete()
    return is_answer


def _get_language(call_data: str, buttons: AppButtons) -> str:
    """
    The _get_language is a helper function is used to determine the language code of a user's Telegram account.
    The function takes two arguments: call_data and buttons. The call_data argument is a string that
    represents the data associated with an inline keyboard button, while the buttons argument represents
    the AppButtons class from app/buttons.py, which contains all of our custom-made inline keyboard button data.

    :param call_data: str: Callback data from the callback query object
    :param buttons: AppButtons: Get the buttons from the middleware
    :return: The language code
    """
    if call_data in (buttons.settings_btn_source.RUSSIA.name, buttons.settings_btn_source.X_RUSSIA.name):
        lang_code: str = settings.RU_LANG_CODE
    else:
        lang_code: str = settings.EN_LANG_CODE
    return lang_code


async def _get_right_markup(buttons: AppButtons, i18n: TranslatorRunner, local: str) -> InlineKeyboardMarkup:
    """
    The _get_right_markup function is a helper function that returns the right markup for the user.
    It checks if the local language of the user is Russian or English and returns either an InlineKeyboardMarkup
    object with Russian buttons or an InlineKeyboardMarkup object with English buttons.

    :param buttons: AppButtons: Get the buttons from the middleware
    :param i18n: TranslatorRunner: Get the language of the user from the middleware. Translate the text of buttons
    :param local: str: Determine the language of the message
    :return: A markup for the language that is set in the settings
    """
    if local == settings.RU_LANG_CODE:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            buttons=await buttons.settings_btn_source.ru_language_menu(),
            i18n=i18n
        )
        return markup
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(
            buttons=await buttons.settings_btn_source.en_language_menu(),
            i18n=i18n
        )
        return markup
