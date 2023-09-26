from aiogram.fsm.state import StatesGroup, State


class CategoryState(StatesGroup):
    GET_NAME = State()
    WAIT_CATEGORY_DATA = State()


class ActionState(StatesGroup):
    WAIT_CATEGORY_DATA = State()
    GET_NAME = State()
    UPDATE_NAME = State()


class TrackerState(StatesGroup):
    WAIT_CATEGORY_DATA = State()
