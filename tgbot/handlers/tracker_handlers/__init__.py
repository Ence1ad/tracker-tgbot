from aiogram import F, Router

from tgbot.keyboards.app_buttons import AppButtons


def register_tracker_handlers() -> Router:
    from .del_tracker import del_tracking_data, take_traker_4_delete
    from .stop_tracker import stop_tracker_yes_handler
    from tgbot.handlers.tracker_handlers.create_tracker import take_action_4_tracker
    from tgbot.handlers.tracker_handlers.create_tracker import pass_tracker_checks
    from .started_tracker import select_launched_tracker
    from .read_tracker import get_tracker_options
    from tgbot.handlers.tracker_handlers.stop_tracker import stop_tracker_no_handler
    from .create_tracker import create_new_tracker
    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation, TrackerCD, \
        TrackerOperation, ActionCD, ActionOperation
    from tgbot.utils.states import TrackerState

    router = Router()

    router.callback_query.register(get_tracker_options, (F.data == AppButtons.general_data.TRACKERS_BTN.name)
                                   | (F.data == AppButtons.trackers_data.DURATION_TRACKER_BTN.name))
    router.callback_query.register(pass_tracker_checks,
                                   F.data == AppButtons.trackers_data.START_TRACKER_BTN.name)
    router.callback_query.register(take_action_4_tracker,
                                   CategoryCD.filter(F.operation == CategoryOperation.READ_TRACKER))
    router.callback_query.register(create_new_tracker, ActionCD.filter(F.operation == ActionOperation.READ_TRACKER),
                                   TrackerState.WAIT_CATEGORY_DATA)
    router.callback_query.register(select_launched_tracker,
                                   F.data == AppButtons.trackers_data.STOP_TRACKER_BTN.name)
    router.callback_query.register(stop_tracker_yes_handler, F.data == AppButtons.general_data.YES_BTN.name)
    router.callback_query.register(stop_tracker_no_handler, F.data == AppButtons.general_data.NO_BTN.name)
    router.callback_query.register(take_traker_4_delete, F.data == AppButtons.trackers_data.DELETE_TRACKER_BTN.name)
    router.callback_query.register(del_tracking_data, TrackerCD.filter(F.operation == TrackerOperation.DEL))

    return router
