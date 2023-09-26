from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import redis_delete_tracker
from db.actions.actions_db_commands import delete_action
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.callback_factories import ActionCD


async def del_action(call: CallbackQuery, callback_data: ActionCD, db_session: async_sessionmaker[AsyncSession],
                     redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    user_id = call.from_user.id
    action_id = callback_data.action_id
    action_name = callback_data.action_name
    markup = await menu_inline_kb(await buttons.action_menu_buttons(), i18n)
    await redis_delete_tracker(user_id, redis_client)
    db_returning = await delete_action(user_id, action_id, db_session)
    if db_returning:
        return await call.message.edit_text(text=i18n.get('rm_action_text', action_name=action_name),
                                            reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('action_not_exists_text'), reply_markup=markup)
