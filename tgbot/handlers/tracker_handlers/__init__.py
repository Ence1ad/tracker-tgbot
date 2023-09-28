from aiogram import F, Router


def register_tracker_handlers() -> Router:
    """
    The register_tracker_handlers function is a router that handles all the trackers related callbacks.
    It registers handlers for:
        - displaying the main menu of trackers;
        - displaying active the user's tracker;
        - creating/updating/deleting a tracker;

    :return: A router object
    """
    from .create_tracker import create_new_tracker, pass_tracker_checks, take_action_4_tracker
    from .read_tracker import trackers_main_menu_handler
    from .update_tracker import check_is_launched_tracker, stop_tracker_yes_handler, stop_tracker_no_handler
    from .delete_tracker import delete_tracker_handler, take_traker_4_delete
    from tgbot.keyboards.app_buttons import AppButtons
    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation, TrackerCD, \
        TrackerOperation, ActionCD, ActionOperation
    from tgbot.utils.states import TrackerState

    router = Router()

    router.callback_query.register(trackers_main_menu_handler, (F.data == AppButtons.general_data.TRACKERS_BTN.name)
                                   | (F.data == AppButtons.trackers_data.DURATION_TRACKER_BTN.name))
    router.callback_query.register(pass_tracker_checks,
                                   F.data == AppButtons.trackers_data.START_TRACKER_BTN.name)
    router.callback_query.register(take_action_4_tracker,
                                   CategoryCD.filter(F.operation == CategoryOperation.READ_TRACKER))
    router.callback_query.register(create_new_tracker, ActionCD.filter(F.operation == ActionOperation.READ_TRACKER),
                                   TrackerState.WAIT_CATEGORY_DATA)
    router.callback_query.register(check_is_launched_tracker,
                                   F.data == AppButtons.trackers_data.STOP_TRACKER_BTN.name)
    router.callback_query.register(stop_tracker_yes_handler, F.data == AppButtons.general_data.YES_BTN.name)
    router.callback_query.register(stop_tracker_no_handler, F.data == AppButtons.general_data.NO_BTN.name)
    router.callback_query.register(take_traker_4_delete, F.data == AppButtons.trackers_data.DELETE_TRACKER_BTN.name)
    router.callback_query.register(delete_tracker_handler, TrackerCD.filter(F.operation == TrackerOperation.DEL))

    return router
