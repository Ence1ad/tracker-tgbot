from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cache.redis_tracker_commands import redis_upd_tracker, is_redis_hexists_tracker
from db.categories.categories_commands import update_category, select_categories, select_category_id
from tgbot.utils.validators import valid_name
from tgbot.keyboards.inline_kb import callback_factories_kb, menu_inline_kb
from tgbot.keyboards.app_buttons import AppButtons
from tgbot.keyboards.callback_factories import CategoryOperation, CategoryCD
from tgbot.utils.states import CategoryState


async def prompt_category_name(call: CallbackQuery, state: FSMContext, callback_data: CategoryCD, i18n: TranslatorRunner
                               ) -> Message:
    category_id: int = callback_data.category_id
    category_name: str = callback_data.category_name
    await state.update_data(category_id=category_id, old_category_name=category_name)
    await state.set_state(CategoryState.WAIT_CATEGORY_DATA)
    return await call.message.edit_text(text=i18n.get('new_category_text'))


async def upd_category_name(message: Message, state: FSMContext, db_session: async_sessionmaker[AsyncSession],
                             i18n: TranslatorRunner, buttons: AppButtons, redis_client: Redis) -> Message | FSMContext:
    await message.delete()
    await state.update_data(category_name=message.text)
    user_id: int = message.from_user.id
    state_data = await state.get_data()
    category_id: int = state_data['category_id']
    new_category_name: str = state_data['category_name']
    old_category_name = state_data['old_category_name']
    # Is the text checking
    markup = await menu_inline_kb(await buttons.category_menu_buttons(), i18n)
    await state.clear()
    if not isinstance(new_category_name, str):
        return await message.answer(text=i18n.get('valid_category_name_text', new_line='\n'), reply_markup=markup)

    elif await select_category_id(user_id=user_id, category_name=old_category_name, db_session=db_session):
        categories = await select_categories(user_id, db_session)  # If message a text
        if new_category_valid_name := await valid_name(categories, new_category_name):
            await update_category(user_id, category_id, new_category_valid_name, db_session)
            await redis_upd_tracker(user_id, redis_client, category_name=new_category_name)
            return await message.answer(text=i18n.get('upd_category_text', new_category_name=new_category_name),
                                        reply_markup=markup)
        else:
            return await message.answer(text=i18n.get('category_exists_text', new_line='\n',
                                                      new_category_name=new_category_name), reply_markup=markup)
    else:
        return await message.answer(text=i18n.get('valid_data_text'), reply_markup=markup)
