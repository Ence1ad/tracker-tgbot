from aiogram import F

from tgbot.handlers.actions_handlers.category_actions import select_category
from tgbot.handlers.actions_handlers.delete_actions import select_remove_action, del_action
from tgbot.handlers.actions_handlers.show_actions import get_actions_options, display_actions
from tgbot.handlers.actions_handlers.new_actions import new_action_reaction_handler, create_action_handler
from tgbot.handlers.actions_handlers.update_actions import update_action_reaction_handler, select_action, upd_action

from tgbot.keyboards.callback_factories import CategoryCD, CategoryOperation, ActionCD, ActionOperation
from tgbot.utils.states import ActionState, UpdateActionState


def register_actions_handlers(router):
    router.callback_query.register(select_category, F.data == 'actions_btn')
    router.callback_query.register(get_actions_options, CategoryCD.filter(F.operation == CategoryOperation.READ))
    router.callback_query.register(display_actions, F.data == 'user_actions')
    router.callback_query.register(new_action_reaction_handler, F.data == 'create_actions')
    router.message.register(create_action_handler, ActionState.GET_NAME)
    router.callback_query.register(select_remove_action, F.data == 'delete_actions')
    router.callback_query.register(del_action, ActionCD.filter(F.operation == ActionOperation.DEL))
    router.callback_query.register(update_action_reaction_handler, F.data == 'update_actions')
    router.callback_query.register(select_action, ActionCD.filter(F.operation == ActionOperation.UDP))
    router.message.register(upd_action, UpdateActionState.GET_NAME)
