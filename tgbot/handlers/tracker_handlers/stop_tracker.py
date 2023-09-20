from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import redis_delete_tracker, redis_hget_tracker_data
from db.tracker.tracker_db_command import select_tracker_duration
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.utils.answer_text import started_tracker_text


async def stop_tracker_handler(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession], redis_client: Redis,
                               buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    user_id: int = call.from_user.id
    tracker_id = int(await redis_hget_tracker_data(user_id, redis_client, 'tracker_id'))
    await call.message.delete()
    if tracker_id:
        markup = await menu_inline_kb(await buttons.tracker_menu_start(), i18n)
        await select_tracker_duration(user_id=user_id, tracker_id=tracker_id, db_session=db_session)
        track_text = await started_tracker_text(user_id=user_id, redis_client=redis_client, i18n=i18n,
                                                title='stop_tracker_text')
        # delete tracker from redis db
        await redis_delete_tracker(user_id, redis_client)
        return await call.message.answer(text=track_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(await buttons.tracker_menu_stop(), i18n)
        return await call.message.edit_text(text=i18n.get('not_launched_tracker_text'), reply_markup=markup)
