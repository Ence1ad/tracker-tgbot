from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.categories.categories_commands import update_category
from tgbot.handlers.categories_handlers import show_user_category
from tgbot.keyboards.categories_kb import list_categories_inline_kb
from tgbot.utils.answer_text import upd_category_text, new_category_text, select_category_text, empty_categories_text
from tgbot.utils.states import UpdateCategoryState


class UpdateCategoryCallback(CallbackData, prefix="udp"):
    category_id: int
    category_name: str


async def select_category(call: CallbackQuery, state: FSMContext, callback_data: UpdateCategoryCallback):
    await call.message.delete()
    await call.message.answer(text=new_category_text)
    await state.update_data(category_id=callback_data.category_id)
    await state.set_state(UpdateCategoryState.GET_NAME)


async def select_update_category(call: CallbackQuery, state: FSMContext):
    categories: list = list(await show_user_category(call))
    if categories:
        markup = await list_categories_inline_kb(categories, UpdateCategoryCallback)
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
