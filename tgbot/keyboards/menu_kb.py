from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.keyboards.buttons_names import exit_btn


async def menu_inline_kb(buttons: dict) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    for data, txt in buttons.items():
        kb_builder.button(text=txt, callback_data=data)
    kb_builder.button(text=exit_btn, callback_data=exit_btn)
    kb_builder.adjust(2, 2)
    return kb_builder.as_markup()


# async def exit_inline_kb() -> InlineKeyboardMarkup:
#     kb_builder = InlineKeyboardBuilder()
#     kb_builder.button(text=exit_btn, callback_data=exit_btn)
#     kb_builder.adjust(1, 1)
#     return kb_builder.as_markup()
