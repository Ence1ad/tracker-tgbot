from aiogram.fsm.state import StatesGroup, State


class CategoryState(StatesGroup):
    """States for category-related actions."""

    GET_NAME = State()
    WAIT_CATEGORY_DATA = State()


class ActionState(StatesGroup):
    """States for action-related actions."""

    WAIT_CATEGORY_DATA = State()
    GET_NAME = State()
    UPDATE_NAME = State()


class TrackerState(StatesGroup):
    """States for tracker-related actions."""

    WAIT_CATEGORY_DATA = State()
