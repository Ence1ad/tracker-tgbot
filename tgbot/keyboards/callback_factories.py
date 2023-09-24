import enum

from aiogram.filters.callback_data import CallbackData


class CategoryOperation(enum.IntEnum):
    READ = 0
    UPD = 1
    DEL = 2
    READ_TRACKER = 3


class ActionOperation(enum.IntEnum):
    READ = 0
    UPD = 1
    DEL = 2
    READ_TRACKER = 3


class TrackerOperation(enum.IntEnum):
    DEL = 0


class CategoryCD(CallbackData, prefix="cat"):
    operation: CategoryOperation
    category_id: int
    category_name: str


class ActionCD(CallbackData, prefix="act"):
    operation: ActionOperation
    action_id: int
    action_name: str


class TrackerCD(CallbackData, prefix="tra"):
    operation: TrackerOperation
    tracker_id: int
