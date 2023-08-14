from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# from tgbot.keyboards.buttons_names import user_actions, create_actions, update_actions, delete_actions
#
#
# async def actions_inline_kb() -> InlineKeyboardMarkup:
#     kb_builder = InlineKeyboardBuilder()
#     kb_builder.button(text=user_actions, callback_data=user_actions)
#     kb_builder.button(text=create_actions, callback_data=create_actions)
#     kb_builder.button(text=update_actions, callback_data=update_actions)
#     kb_builder.button(text=delete_actions, callback_data=delete_actions)
#     kb_builder.adjust(2, 2)
#     return kb_builder.as_markup()


async def list_actions_inline_kb(actions: list, callback_class) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for act in actions:
        kb_builder.button(
            text=f"{act.action_name}",
            callback_data=callback_class(action_id=act.action_id, action_name=act.action_name)
        )
    kb_builder.adjust(3)
    return kb_builder.as_markup()

