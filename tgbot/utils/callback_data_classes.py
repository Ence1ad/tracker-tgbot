from aiogram.filters.callback_data import CallbackData

class DeleteCategoryCallback(CallbackData, prefix="del"):
    category_id: int
    category_name: str

class UpdateCategoryCallback(CallbackData, prefix="udp"):
    category_id: int
    category_name: str

class SelectCategoryCallback(CallbackData, prefix="sel"):
    category_id: int
    category_name: str


class DeleteActionCallback(CallbackData, prefix="del_act"):
    action_id: int
    action_name: str


class UpdateActionCallback(CallbackData, prefix="udp_act"):
    action_id: int
    action_name: str

class SelectCategoryTrackerCallback(CallbackData, prefix="sel_tra"):
    category_id: int
    category_name: str

class SelectActionTrackerCallback(CallbackData, prefix="sel_act"):
    action_id: int
    action_name: str

