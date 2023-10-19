from aiogram import F, Router


def register_tracker_handlers() -> Router:
    """Register handlers for tracker-related operations.

    This function configures handlers for tracker operations, including starting,
    stopping, creating, and deleting trackers.

    Handlers Description:
    - `trackers_main_menu_handler`: Handles displaying the main menu for trackers.
    - `pass_tracker_checks`: Handles checking conditions for starting a tracker.
    - `take_action_4_tracker`: Handles selecting actions for a tracker.
    - `create_new_tracker`: Handles creating a new tracker.
    - `check_is_launched_tracker`: Handles checking if a tracker is already running.
    - `stop_tracker_yes_handler`: Handles confirming to stop a running tracker.
    - `stop_tracker_no_handler`: Handles canceling the action to stop a running tracker.
    - `take_traker_4_delete`: Handles selecting a tracker to delete.
    - `delete_tracker_handler`: Handles deleting a tracker.
    :return: Router: A configured Router object with the registered handlers.
    """
    from .create_tracker import create_new_tracker, pass_tracker_checks, \
        take_action_4_tracker
    from .read_tracker import trackers_main_menu_handler
    from .update_tracker import check_is_launched_tracker, stop_tracker_yes_handler, \
        stop_tracker_no_handler
    from .delete_tracker import delete_tracker_handler, take_traker_4_delete
    from tgbot.keyboards.app_buttons import AppButtons
    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation, \
        TrackerCD, \
        TrackerOperation, ActionCD, ActionOperation
    from tgbot.utils.states import TrackerState

    router = Router()

    router.callback_query.register(
        trackers_main_menu_handler,
        (F.data == AppButtons.general_btn_source.TRACKERS_BTN.name) |
        (F.data == AppButtons.trackers_btn_source.DURATION_TRACKER_BTN.name))
    router.callback_query.register(
        pass_tracker_checks,
        F.data == AppButtons.trackers_btn_source.START_TRACKER_BTN.name
    )
    router.callback_query.register(take_action_4_tracker,
                                   CategoryCD.filter(
                                       F.operation == CategoryOperation.READ_TRACKER))
    router.callback_query.register(create_new_tracker, ActionCD.filter(
        F.operation == ActionOperation.READ_TRACKER),
                                   TrackerState.WAIT_CATEGORY_DATA)
    router.callback_query.register(
        check_is_launched_tracker,
        F.data == AppButtons.trackers_btn_source.STOP_TRACKER_BTN.name
    )
    router.callback_query.register(stop_tracker_yes_handler,
                                   F.data == AppButtons.general_btn_source.YES_BTN.name)
    router.callback_query.register(stop_tracker_no_handler,
                                   F.data == AppButtons.general_btn_source.NO_BTN.name)
    router.callback_query.register(
        take_traker_4_delete,
        F.data == AppButtons.trackers_btn_source.DELETE_TRACKER_BTN.name
    )
    router.callback_query.register(delete_tracker_handler, TrackerCD.filter(
        F.operation == TrackerOperation.DEL))

    return router
