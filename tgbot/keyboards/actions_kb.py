from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def list_actions_inline_kb(actions: list, callback_class) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for act in actions:
        kb_builder.button(
            text=f"{act.Actions.action_name}",
            callback_data=callback_class(action_id=act.Actions.action_id, action_name=act.Actions.action_name)
        )
    kb_builder.adjust(3)
    return kb_builder.as_markup()
