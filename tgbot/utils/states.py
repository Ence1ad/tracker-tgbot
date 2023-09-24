from aiogram.fsm.state import StatesGroup, State


class CategoryState(StatesGroup):
    GET_NAME = State()
    WAIT_CATEGORY_DATA = State()


class ActionState(StatesGroup):
    WAIT_CATEGORY_DATA = State()
    GET_NAME = State()
    CATEGORY_ID = State()


class UpdateActionState(StatesGroup):
    GET_NAME = State()


class TrackerState(StatesGroup):
    WAIT_CATEGORY_DATA = State()
