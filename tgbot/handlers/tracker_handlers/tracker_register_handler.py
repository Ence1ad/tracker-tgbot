from aiogram import F

from .daily_tracker import report_daily_tracking
from .del_tracker import del_tracking_data
from .stop_tracker import stop_tracker_handler
from .actions_tracker import display_actions_tracker
from .categories_tracker import select_category_tracker
from .launched import select_launched_tracker
from .menu_tracker import get_tracker_options, no_btn_handler
from .new_tracker import create_new_tracker
from tgbot.keyboards.buttons_names import trackers_btn, new_tracker_btn, launched_btn, yes_btn, no_btn, \
    delete_tracker_btn, day_track_btn
from tgbot.utils.callback_data_classes import SelectCategoryTrackerCallback, SelectActionTrackerCallback


def register_tracker_handlers(router):
    router.callback_query.register(get_tracker_options, F.data == trackers_btn)
    router.callback_query.register(select_category_tracker, F.data == new_tracker_btn)
    router.callback_query.register(display_actions_tracker, SelectCategoryTrackerCallback.filter())
    router.callback_query.register(create_new_tracker, SelectActionTrackerCallback.filter())
    router.callback_query.register(select_launched_tracker, F.data == launched_btn)
    router.callback_query.register(stop_tracker_handler, F.data == yes_btn)
    router.callback_query.register(no_btn_handler, F.data == no_btn)
    router.callback_query.register(del_tracking_data, F.data == delete_tracker_btn)
    router.callback_query.register(report_daily_tracking, F.data == day_track_btn)
    # router.callback_query.register(select_action, UpdateActionCallback.filter())
    # router.message.register(upd_action, UpdateActionState.GET_NAME)