from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_commands import redis_upd_tracker
from db.categories.categories_commands import update_category, select_categories
from tgbot.utils.validators import valid_name
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.keyboards.buttons_names import category_menu_buttons, new_category_button
from tgbot.utils.answer_text import upd_category_text, new_category_text, select_category_text, empty_categories_text, \
    categories_is_fake_text, accept_only_text, category_exists_text
from tgbot.keyboards.callback_factories import CategoryOperation, CategoryCD
from tgbot.utils.states import UpdateCategoryState


async def select_update_category(call: CallbackQuery, db_session: async_sessionmaker[AsyncSession]) -> Message:
    user_id = call.from_user.id
    categories = await select_categories(user_id, db_session)
    if categories:
        markup = await callback_factories_kb(categories, CategoryOperation.UDP)
        return await call.message.edit_text(text=select_category_text, reply_markup=markup)
    else:
        markup = await menu_inline_kb(new_category_button)
        return await call.message.edit_text(text=empty_categories_text, reply_markup=markup)


async def select_category(call: CallbackQuery, state: FSMContext, callback_data: CategoryCD) -> None:
    await call.message.edit_text(text=new_category_text)
    category_id: int = callback_data.category_id
    await state.update_data(category_id=category_id, category_old_name=callback_data.category_name)
    await state.set_state(UpdateCategoryState.WAIT_CATEGORY_DATA)


async def upd_category(message: Message, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                       redis_client: Redis) -> Message:
    await message.delete()
    await state.update_data(category_name=message.text)
    user_id: int = message.from_user.id
    state_data = await state.get_data()
    new_category_name: str = state_data['category_name']

    # Is the text checking
    if not isinstance(new_category_name, str):
        await message.answer(text=f"{accept_only_text}")

    else:  # If message a text
        categories = await select_categories(user_id, db_session)
        new_category_valid_name = await valid_name(categories, new_category_name)

        if new_category_valid_name:
            await state.clear()
            await _udp_category(message=message, db_session=db_session, redis_client=redis_client,
                                new_category_name=new_category_valid_name, state_data=state_data)
        else:
            return await message.answer(text=f"{new_category_name} {category_exists_text}")


async def _udp_category(message: Message, db_session: async_sessionmaker[AsyncSession],
                        redis_client: Redis, new_category_name: str, state_data: dict[str: Any]) -> Message:
    user_id = message.from_user.id
    category_id: int = state_data['category_id']
    category_old_name = state_data['category_old_name']
    returning = await update_category(user_id, category_id, new_category_name, db_session)
    markup = await menu_inline_kb(category_menu_buttons)
    if returning:
        await redis_upd_tracker(user_id, redis_client, category_name=new_category_name)
        return await message.answer(text=f"{upd_category_text} {category_old_name} -> {new_category_name}",
                                    reply_markup=markup)
    else:
        return await message.answer(text=categories_is_fake_text, reply_markup=markup)
