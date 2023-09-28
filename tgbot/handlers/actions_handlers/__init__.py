from aiogram import F, Router

from tgbot.handlers.actions_handlers.read_actions import collect_actions_data_handler


def register_actions_handlers() -> Router:
    """
    The register_actions_handlers function is a router that handles all the actions related callbacks.
    It registers handlers for:
        - displaying the main menu of actions;
        - displaying all the user's actions;
        - prompting for a new action name to be created/updated;
        - creating/updating/deleting an action with a given name and category id (category_id is passed in as callback data);

    :return: A router object

    """
    from .delete_actions import delete_action_handler
    from .read_actions import actions_main_menu_handler, display_actions
    from .create_actions import prompt_name_4_new_action_handler, create_action_handler
    from .update_actions import prompt_new_action_name, update_action_name_handler
    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation, ActionCD, ActionOperation
    from tgbot.keyboards.app_buttons import AppButtons
    from tgbot.utils.states import ActionState

    router = Router()

    router.callback_query.register(actions_main_menu_handler, CategoryCD.filter(F.operation == CategoryOperation.READ))
    router.callback_query.register(display_actions, (F.data == AppButtons.actions_data.USER_ACTIONS.name),
                                   ActionState.WAIT_CATEGORY_DATA)
    router.callback_query.register(prompt_name_4_new_action_handler, (F.data == AppButtons.actions_data.CREATE_ACTIONS.name),
                                   ActionState.WAIT_CATEGORY_DATA)
    router.message.register(create_action_handler, ActionState.GET_NAME)

    router.callback_query.register(collect_actions_data_handler, F.data == AppButtons.actions_data.UPDATE_ACTIONS.name,
                                   ActionState.WAIT_CATEGORY_DATA)
    router.callback_query.register(prompt_new_action_name, ActionCD.filter(F.operation == ActionOperation.UPD))
    router.message.register(update_action_name_handler, ActionState.UPDATE_NAME)
    router.callback_query.register(collect_actions_data_handler, (F.data == AppButtons.actions_data.DELETE_ACTIONS.name),
                                   ActionState.WAIT_CATEGORY_DATA)
    router.callback_query.register(delete_action_handler, ActionCD.filter(F.operation == ActionOperation.DEL))

    return router
