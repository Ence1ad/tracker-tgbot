from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.redis_language_commands import redis_hget_lang
from config import settings
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb


async def command_settings_handler(message: Message, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    markup: InlineKeyboardMarkup = await menu_inline_kb(buttons=await buttons.settings_menu(), i18n=i18n)
    await message.delete()
    return await message.answer(text=i18n.get('options_text'), reply_markup=markup)


async def set_user_language(call: CallbackQuery, buttons: AppButtons, i18n: TranslatorRunner, redis_client: Redis
                            ) -> Message:
    user_id = call.from_user.id
    local = await redis_hget_lang(user_id, redis_client=redis_client)
    markup: InlineKeyboardMarkup = await _get_right_markup(buttons=buttons, i18n=i18n,
                                                           redis_client=redis_client, local=local)

    return await call.message.edit_text(text=i18n.get('select_lang_text'), reply_markup=markup)


async def set_ru_lang(call: CallbackQuery, redis_client: Redis, i18n: TranslatorRunner) -> bool:
    user_id: str = str(call.from_user.id)
    lang_code = settings.RU_LANG_CODE
    await redis_client.hset(name='lang', key=user_id, value=lang_code)
    msg = await call.answer(text=i18n.get('set_lang_text'), show_alert=True)
    await call.message.delete()
    return msg


async def set_en_lang(call: CallbackQuery, redis_client: Redis, i18n: TranslatorRunner) -> bool:
    user_id: str = str(call.from_user.id)
    lang_code = settings.EN_LANG_CODE
    await redis_client.hset(name='lang', key=user_id, value=lang_code)
    msg = await call.answer(text=i18n.get('set_lang_text'), show_alert=True)
    await call.message.delete()
    return msg


async def _get_right_markup(buttons: AppButtons, redis_client: Redis, i18n: TranslatorRunner,
                            local: str) -> InlineKeyboardMarkup:

    if local == settings.RU_LANG_CODE:
        markup: InlineKeyboardMarkup = await menu_inline_kb(buttons=await buttons.ru_language_menu(), i18n=i18n)
    else:
        markup: InlineKeyboardMarkup = await menu_inline_kb(buttons=await buttons.en_language_menu(), i18n=i18n)
    return markup

