from aiogram import F, Router

from tgbot.keyboards.app_buttons import AppButtons


def register_tracker_handlers() -> Router:
    from .del_tracker import del_tracking_data, select_removing_tracker
    from .stop_tracker import stop_tracker_handler
    from .tracker_actions import display_actions_tracker
    from .tracker_categories import select_category_tracker
    from .started_tracker import select_launched_tracker
    from .menu_tracker import get_tracker_options, no_btn_handler
    from .new_tracker import create_new_tracker
    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation, TrackerCD, \
        TrackerOperation, ActionCD, ActionOperation
    from tgbot.utils.states import TrackerState

    router = Router()

    router.callback_query.register(get_tracker_options, (F.data == AppButtons.general_data.TRACKERS_BTN.name)
                                   | (F.data == AppButtons.trackers_data.DURATION_TRACKER_BTN.name))
    router.callback_query.register(select_category_tracker,
                                   F.data == AppButtons.trackers_data.START_TRACKER_BTN.name)
    router.callback_query.register(display_actions_tracker,
                                   CategoryCD.filter(F.operation == CategoryOperation.READ_TRACKER))
    router.callback_query.register(create_new_tracker, ActionCD.filter(F.operation == ActionOperation.READ_TRACKER),
                                   TrackerState.WAIT_CATEGORY_DATA)
    router.callback_query.register(select_launched_tracker,
                                   F.data == AppButtons.trackers_data.STOP_TRACKER_BTN.name)
    router.callback_query.register(stop_tracker_handler, F.data == AppButtons.general_data.YES_BTN.name)
    router.callback_query.register(no_btn_handler, F.data == AppButtons.general_data.NO_BTN.name)
    router.callback_query.register(select_removing_tracker, F.data == AppButtons.trackers_data.DELETE_TRACKER_BTN.name)
    router.callback_query.register(del_tracking_data, TrackerCD.filter(F.operation == TrackerOperation.DEL))

    return router
