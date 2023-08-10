from telethon.tl.types import KeyboardButtonRow, ReplyInlineMarkup, KeyboardButtonUrl, KeyboardButtonCallback, \
    KeyboardButton
from tgbot.buttons_names import my_categories, create_categories, update_categories, delete_categories
from telethon.tl.custom.button import Button


async def categories_inline_kb() -> ReplyInlineMarkup:
    inline_keyboard = ReplyInlineMarkup(
        [
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(text=my_categories,
                                           data=b'my_categories'),
                    KeyboardButtonCallback(text=create_categories,
                                           data=b'create_categories'
                                           ),

                ]
            ),
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(text=update_categories,
                                           data=b'update_categories'),
                    KeyboardButtonCallback(text=delete_categories,
                                           data=b'delete_categories'),

                ]
            ),
        ]
    )
    return inline_keyboard


# def show_options_kb(lst: list) -> ReplyInlineMarkup:
async def show_options_kb(lst: list) -> ReplyInlineMarkup:
    buttons = []
    for title in lst:
        buttons.append(Button.inline(text=title, data=title))
    markup = await buttons_each_rows(buttons, 3)
    return markup


async def buttons_each_rows(buttons, row_num) -> ReplyInlineMarkup:
    kb_row = []
    buttons_in_row = []
    btn_cnt = len(buttons)
    while btn_cnt > 0:
        if btn_cnt < row_num:
            kb_row.append(KeyboardButtonRow(buttons))
            break
        if btn_cnt % row_num != 0:
            kb = buttons.pop()
            kb_row.append(KeyboardButtonRow([kb]))
            btn_cnt -= 1

        for idx, button in enumerate(buttons, 1):
            buttons_in_row.append(button)
            if idx % row_num == 0:
                kb_row.append(KeyboardButtonRow(buttons_in_row))
                buttons_in_row = []
                btn_cnt -= row_num
    markup = ReplyInlineMarkup(rows=kb_row)
    return markup
