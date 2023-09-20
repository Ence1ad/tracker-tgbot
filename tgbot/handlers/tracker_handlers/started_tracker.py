from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.redis_tracker_commands import is_redis_hexists_tracker
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.utils.answer_text import started_tracker_text


async def select_launched_tracker(call: CallbackQuery, redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner
                                  ) -> Message:
    user_id = call.from_user.id
    is_tracker = await is_redis_hexists_tracker(user_id, redis_client)
    if is_tracker:
        started_tracker = await started_tracker_text(user_id=user_id, redis_client=redis_client, i18n=i18n,
                                                     title='started_tracker_title')
        await call.message.delete()
        markup = await menu_inline_kb(await buttons.yes_no_menu(), i18n)
        return await call.message.answer(text=started_tracker + i18n.get('answer_stop_tracker_text'),
                                         reply_markup=markup)
    else:
        await call.message.delete()
        markup = await menu_inline_kb(await buttons.tracker_menu_start(), i18n)
        return await call.message.answer(text=i18n.get('not_launched_tracker_text'), reply_markup=markup)
