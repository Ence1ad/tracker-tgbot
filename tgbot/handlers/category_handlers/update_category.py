from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.categories.categories_commands import update_category
from tgbot.handlers.category_handlers import show_user_category
from tgbot.keyboards.categories_kb import update_category_inline_kb, UpdateCategoryCallback
from tgbot.utils.answer_text import upd_category_text, new_category_text, select_category_text, empty_categories_text
from tgbot.utils.states import UpdateCategoryState


async def select_category(call: CallbackQuery, state: FSMContext, callback_data: UpdateCategoryCallback):
    await call.message.delete()
    await call.message.answer(text=new_category_text)
    await state.update_data(category_id=callback_data.category_id)
    await state.set_state(UpdateCategoryState.GET_NAME)


async def select_update_category(call: CallbackQuery, state: FSMContext):
    categories: list = list(await show_user_category(call))
    if categories:
        markup = await update_category_inline_kb(categories)
        await call.message.answer(text=select_category_text, reply_markup=markup)
        await state.set_state(UpdateCategoryState.GET_NAME)
    else:
        await call.message.answer(text=empty_categories_text)


async def upd_category(message: Message, state: FSMContext):
    await state.update_data(category_name=message.text)
    user_id = message.from_user.id
    state_data = await state.get_data()
    await state.clear()
    new_category_name = state_data['category_name'].strip()[:29]
    await update_category(user_id, state_data['category_id'], new_category_name)
    await message.answer(text=f"{upd_category_text} {new_category_name}")
