from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_commands import redis_hget_tracker_data, redis_delete_tracker
from db.categories.categories_commands import delete_category, select_categories
from tgbot.keyboards.buttons_names import category_menu_buttons, new_category_button
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.utils.answer_text import rm_category_text, select_category_text, empty_categories_text, \
    categories_is_fake_text
from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation


async def select_remove_category(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession]) -> Message:
    user_id = call.from_user.id
    categories = await select_categories(user_id, db_session)
    if categories:
        markup = await callback_factories_kb(categories, CategoryOperation.DEL)
        return await call.message.edit_text(text=select_category_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(new_category_button)
        return await call.message.edit_text(text=empty_categories_text, reply_markup=markup)


async def del_category(call: CallbackQuery, callback_data: CategoryCD, db_session: async_sessionmaker[AsyncSession],
                       redis_client: Redis) -> Message:
    user_id = call.from_user.id
    category_id = callback_data.category_id
    category_name = callback_data.category_name
    markup = await menu_inline_kb(category_menu_buttons)
    await redis_hget_tracker_data(user_id, redis_client, key="category_id") and await redis_delete_tracker(user_id,
                                                                                                           redis_client)
    returning = await delete_category(user_id, category_id, db_session)
    if returning:
        return await call.message.edit_text(text=f"{rm_category_text} {category_name}", reply_markup=markup)
    else:
        return await call.message.edit_text(text=categories_is_fake_text, reply_markup=markup)
