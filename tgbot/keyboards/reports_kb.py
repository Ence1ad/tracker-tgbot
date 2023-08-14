# from aiogram.types import InlineKeyboardMarkup
# from aiogram.utils.keyboard import InlineKeyboardBuilder
#
#
# async def menu_inline_kb(buttons: dict) -> InlineKeyboardMarkup:
#     kb_builder = InlineKeyboardBuilder()
#     for data, txt in buttons.items():
#         print(txt)
#         kb_builder.button(text=txt, callback_data=data)
#     kb_builder.adjust(2, 2)
#     return kb_builder.as_markup()
