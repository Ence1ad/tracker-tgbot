import enum

from aiogram.filters.callback_data import CallbackData


class CategoryOperation(enum.IntEnum):
    """Enumeration of category operations."""

    READ = 0
    UPD = 1
    DEL = 2
    READ_TRACKER = 3


class ActionOperation(enum.IntEnum):
    """Enumeration of action operations."""

    READ = 0
    UPD = 1
    DEL = 2
    READ_TRACKER = 3


class TrackerOperation(enum.IntEnum):
    """Enumeration of tracker operations."""

    DEL = 0


class CategoryCD(CallbackData, prefix="cat"):
    """CallbackData class for category-related operations."""

    operation: CategoryOperation
    category_id: int
    category_name: str


class ActionCD(CallbackData, prefix="act"):
    """CallbackData class for action-related operations."""

    operation: ActionOperation
    action_id: int
    action_name: str


class TrackerCD(CallbackData, prefix="tra"):
    """CallbackData class for tracker-related operations."""

    operation: TrackerOperation
    tracker_id: int
