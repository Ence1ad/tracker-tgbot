from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.redis_tracker_commands import is_redis_hexists_tracker
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.utils.answer_text import started_tracker_text
from tgbot.keyboards.inline_kb import menu_inline_kb


async def get_tracker_options(call: CallbackQuery, redis_client: Redis, buttons: AppButtons,
                              i18n: TranslatorRunner) -> Message:
    user_id = call.from_user.id
    await call.message.delete()
    if await is_redis_hexists_tracker(user_id, redis_client):
        started_tracker = await started_tracker_text(user_id=user_id, redis_client=redis_client, i18n=i18n,
                                                     title='started_tracker_title')
        markup = await menu_inline_kb(await buttons.tracker_menu_stop(), i18n)
        return await call.message.answer(text=started_tracker, reply_markup=markup)
    else:
        markup = await menu_inline_kb(await buttons.tracker_menu_start(), i18n)
        return await call.message.answer(text=i18n.get('options_text'), reply_markup=markup)


