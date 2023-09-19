from aiogram import F, Router

from tgbot.keyboards.app_buttons import AppButtons


def register_actions_handlers() -> Router:
    from .category_actions import select_category
    from .delete_actions import select_remove_action, del_action
    from .show_actions import get_actions_options, display_actions
    from .create_actions import prompt_new_action_handler, create_action_handler
    from .update_actions import update_action_reaction_handler, select_action, upd_action
    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation, ActionCD, ActionOperation
    from tgbot.utils.states import ActionState, UpdateActionState

    router = Router()

    router.callback_query.register(select_category, F.data == AppButtons.general_data.ACTIONS_BTN.name)
    router.callback_query.register(get_actions_options, CategoryCD.filter(F.operation == CategoryOperation.READ))
    router.callback_query.register(display_actions, (F.data == AppButtons.actions_data.USER_ACTIONS.name),
                                   ActionState.WAIT_CATEGORY_DATA)
    router.callback_query.register(prompt_new_action_handler, F.data == AppButtons.actions_data.CREATE_ACTIONS.name,
                                   ActionState.WAIT_CATEGORY_DATA)
    router.message.register(create_action_handler, ActionState.GET_NAME)
    router.callback_query.register(select_remove_action, (F.data == AppButtons.actions_data.DELETE_ACTIONS.name),
                                   ActionState.WAIT_CATEGORY_DATA)
    router.callback_query.register(del_action, ActionCD.filter(F.operation == ActionOperation.DEL))
    router.callback_query.register(update_action_reaction_handler, F.data == AppButtons.actions_data.UPDATE_ACTIONS.name,
                                   ActionState.WAIT_CATEGORY_DATA)
    router.callback_query.register(select_action, ActionCD.filter(F.operation == ActionOperation.UDP))
    router.message.register(upd_action, UpdateActionState.GET_NAME)

    return router
