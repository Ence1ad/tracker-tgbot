from aiogram import F, Router


def register_actions_handlers() -> Router:
    """Register handlers for action-related operations.

    This function configures handlers for performing actions related to user-defined
    categories.

    Handlers Description:
    - `actions_main_menu_handler`: Handles displaying the main menu for actions and
    category-specific actions.
    - `display_actions`: Handles displaying the list of user-defined actions for a
    specific category.
    - `prompt_name_4_new_action_handler`: Handles prompting the user for a new action
    name.
    - `create_action_handler`: Handles creating a new user-defined action.
    - `collect_actions_data_handler`: Handles collecting data for updating or deleting
    an action.
    - `prompt_new_action_name`: Handles prompting the user for a new name when updating
     an action.
    - `update_action_name_handler`: Handles updating the name of an existing
    user-defined action.
    - `delete_action_handler`: Handles deleting an existing user-defined action.

    :return: Router: A configured Router object with the registered handlers.
    """
    from .delete_actions import delete_action_handler
    from .read_actions import actions_main_menu_handler, display_actions, \
        collect_actions_data_handler
    from .create_actions import prompt_name_4_new_action_handler, create_action_handler
    from .update_actions import prompt_new_action_name, update_action_name_handler
    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation, \
        ActionCD, ActionOperation
    from tgbot.keyboards.app_buttons import AppButtons
    from tgbot.utils.states import ActionState

    router = Router()

    router.callback_query.register(actions_main_menu_handler, CategoryCD.filter(
        F.operation == CategoryOperation.READ))
    router.callback_query.register(display_actions, (
                F.data == AppButtons.actions_btn_source.USER_ACTIONS.name),
                                   ActionState.WAIT_CATEGORY_DATA)
    router.callback_query.register(
        prompt_name_4_new_action_handler,
        (F.data == AppButtons.actions_btn_source.CREATE_ACTIONS.name),
        ActionState.WAIT_CATEGORY_DATA
    )
    router.message.register(create_action_handler, ActionState.GET_NAME, F.text)

    router.callback_query.register(
        collect_actions_data_handler,
        F.data.in_((AppButtons.actions_btn_source.UPDATE_ACTIONS.name,
                   AppButtons.actions_btn_source.DELETE_ACTIONS.name)),
        ActionState.WAIT_CATEGORY_DATA
    )
    router.callback_query.register(prompt_new_action_name,
                                   ActionCD.filter(F.operation == ActionOperation.UPD))
    router.message.register(update_action_name_handler, ActionState.UPDATE_NAME, F.text)
    router.callback_query.register(delete_action_handler,
                                   ActionCD.filter(F.operation == ActionOperation.DEL))

    return router
