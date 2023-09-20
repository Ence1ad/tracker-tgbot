from aiogram.types import CallbackQuery, Message
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import redis_hget_tracker_data, redis_delete_tracker
from db.categories.categories_commands import delete_category, select_categories
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation


async def pick_removing_category_handler(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession],
                                         buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    user_id = call.from_user.id
    categories = await select_categories(user_id, db_session)
    if categories:
        markup = await callback_factories_kb(categories, CategoryOperation.DEL)
        return await call.message.edit_text(text=i18n.get('select_category_text'), reply_markup=markup)
    else:
        markup = await menu_inline_kb(await buttons.new_category(), i18n)
        return await call.message.edit_text(text=i18n.get('empty_categories_text'), reply_markup=markup)


async def del_category(call: CallbackQuery, callback_data: CategoryCD, db_session: async_sessionmaker[AsyncSession],
                       redis_client: Redis, buttons: AppButtons, i18n: TranslatorRunner) -> Message:
    user_id = call.from_user.id
    category_id = callback_data.category_id
    category_name = callback_data.category_name
    markup = await menu_inline_kb(await buttons.category_menu_buttons(), i18n)
    await redis_hget_tracker_data(user_id, redis_client, key="category_id") and await redis_delete_tracker(user_id,
                                                                                                           redis_client)
    returning = await delete_category(user_id, category_id, db_session)
    if returning:
        return await call.message.edit_text(text=f"{i18n.get('rm_category_text')} {category_name}", reply_markup=markup)
    else:
        return await call.message.edit_text(text=i18n.get('categories_is_fake_text'), reply_markup=markup)
