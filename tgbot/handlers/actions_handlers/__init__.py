from aiogram import F, Router

from tgbot.handlers.actions_handlers.read_actions import get_actions_handler


def register_actions_handlers() -> Router:
    from .delete_actions import del_action
    from .read_actions import get_actions_options, display_actions
    from .create_actions import prompt_new_action_handler, create_action_handler
    from .update_actions import prompt_new_action_name, upd_action
    from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation, ActionCD, ActionOperation
    from tgbot.keyboards.app_buttons import AppButtons
    from tgbot.utils.states import ActionState

    router = Router()

    router.callback_query.register(get_actions_options, CategoryCD.filter(F.operation == CategoryOperation.READ))
    router.callback_query.register(display_actions, (F.data == AppButtons.actions_data.USER_ACTIONS.name),
                                   ActionState.WAIT_CATEGORY_DATA)
    router.callback_query.register(prompt_new_action_handler, (F.data == AppButtons.actions_data.CREATE_ACTIONS.name),
                                   ActionState.WAIT_CATEGORY_DATA)
    router.message.register(create_action_handler, ActionState.GET_NAME)

    router.callback_query.register(get_actions_handler, F.data == AppButtons.actions_data.UPDATE_ACTIONS.name,
                                   ActionState.WAIT_CATEGORY_DATA)
    router.callback_query.register(prompt_new_action_name, ActionCD.filter(F.operation == ActionOperation.UPD))
    router.message.register(upd_action, ActionState.UPDATE_NAME)
    router.callback_query.register(get_actions_handler, (F.data == AppButtons.actions_data.DELETE_ACTIONS.name),
                                   ActionState.WAIT_CATEGORY_DATA)
    router.callback_query.register(del_action, ActionCD.filter(F.operation == ActionOperation.DEL))

    return router
