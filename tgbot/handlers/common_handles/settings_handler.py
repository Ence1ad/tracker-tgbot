from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.language_redis_manager import redis_hget_lang, redis_hset_lang
from config import settings
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb


async def command_settings_handler(message: Message, buttons: AppButtons,
                                   i18n: TranslatorRunner) -> Message:
    """Handle the user's request to access settings by providing a settings menu.

    :param message: Message: The Message object representing the user's request.
    :param buttons: AppButtons: An instance of AppButtons for accessing button data.
    :param i18n: TranslatorRunner: An internationalization runner for text localization.
    :return: Message: A response message containing the settings menu.
    """
    markup: InlineKeyboardMarkup = await menu_inline_kb(
        buttons=await buttons.settings_btn_source.settings_menu(), i18n=i18n
    )
    await message.delete()
    return await message.answer(text=i18n.get('options_text'), reply_markup=markup)


async def language_settings(
        call: CallbackQuery, buttons: AppButtons, i18n: TranslatorRunner,
        redis_client: Redis
) -> Message:
    """Handle the user's request to change the lang setting and provide lang options.

    :param call: CallbackQuery: The CallbackQuery object representing the user's
    request.
    :param buttons: AppButtons: An instance of AppButtons for accessing button data.
    :param i18n: TranslatorRunner: An internationalization runner for text localization.
    :param redis_client: Redis: The Redis client for data storage.
    :return: Message: A response message with language options for the user.
    """
    user_id: int = call.from_user.id
    local: str = await redis_hget_lang(user_id, redis_client=redis_client)
    markup: InlineKeyboardMarkup = await _get_right_markup(buttons=buttons, i18n=i18n,
                                                           local=local)
    return await call.message.edit_text(text=i18n.get('select_lang_text'),
                                        reply_markup=markup)


async def set_user_lang(
        call: CallbackQuery, redis_client: Redis, i18n: TranslatorRunner,
        buttons: AppButtons) -> bool:
    """Set the user's lang preference based on their selection.

    :param call: CallbackQuery: The CallbackQuery object representing the user's
    request.
    :param redis_client: Redis: The Redis client for data storage.
    :param i18n: TranslatorRunner: An internationalization runner for text localization.
    :param buttons: AppButtons: An instance of AppButtons for accessing button data.
    :return: bool: A boolean indicating whether the operation was successful.
    """
    user_id: int = call.from_user.id
    before_lang_code = await redis_hget_lang(user_id, redis_client=redis_client)
    lang_code: str = _get_language(call_data=call.data, buttons=buttons)
    await redis_hset_lang(user_id, lang_code=lang_code, redis_client=redis_client)
    if before_lang_code != lang_code:
        is_answer: bool = await call.answer(text=i18n.get('set_lang_text'),
                                            show_alert=True)
    else:
        is_answer: bool = await call.answer(text=i18n.get('settings_not_change_text'),
                                            show_alert=True)
    await call.message.delete()
    return is_answer


def _get_language(call_data: str, buttons: AppButtons) -> str:
    """Get the language code based on the user's selection.

    :param call_data: str: The callback data provided by the user.
    :param buttons: AppButtons: An instance of AppButtons for accessing button data.
    :return: str: The language code (e.g., "ru" for Russian, "en" for English).
    """
    if call_data in (buttons.settings_btn_source.RUSSIA.name,
                     buttons.settings_btn_source.X_RUSSIA.name):
        lang_code: str = settings.RU_LANG_CODE
    else:
        lang_code: str = settings.EN_LANG_CODE
    return lang_code


async def _get_right_markup(buttons: AppButtons, i18n: TranslatorRunner, local: str
                            ) -> InlineKeyboardMarkup:
    """Get the correct language selection markup based on the user's current language.

    :param buttons: AppButtons: An instance of AppButtons for accessing button data.
    :param i18n: TranslatorRunner: An internationalization runner for text localization.
    :param local: str: The user's current language code.
    :return: InlineKeyboardMarkup: An inline keyboard markup for language selection.
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
