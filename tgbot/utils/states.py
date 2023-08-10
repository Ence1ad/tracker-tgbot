from aiogram.fsm.state import StatesGroup, State


class CategoryState(StatesGroup):
    GET_NAME = State()


class UpdateCategoryState(StatesGroup):
    GET_NAME = State()
    GET_ID = State()
