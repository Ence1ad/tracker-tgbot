from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import redis_delete_tracker
from db.categories.categories_commands import delete_category
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import menu_inline_kb
from tgbot.keyboards.callback_factories import CategoryCD


async def del_category(call: CallbackQuery, callback_data: CategoryCD, db_session: async_sessionmaker[AsyncSession],
                       redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner, state: FSMContext) -> Message:
    user_id = call.from_user.id
    category_id = callback_data.category_id
    markup = await menu_inline_kb(await buttons.category_menu_buttons(), i18n)
    await redis_delete_tracker(user_id, redis_client)
    returning = await delete_category(user_id, category_id, db_session)
    if returning:
        await state.clear()
        return await call.message.edit_text(text=f"{i18n.get('rm_category_text')}", reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('categories_is_fake_text'), reply_markup=markup)
