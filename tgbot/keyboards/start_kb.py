from telethon.tl.types import KeyboardButtonRow, ReplyInlineMarkup, KeyboardButtonUrl, KeyboardButtonCallback
from tgbot.buttons_names import *

def start_kb() -> ReplyInlineMarkup:
    inline_keyboard = ReplyInlineMarkup(
        [
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(text=first_btn,
                                           data=b'some_bytes'),
                    KeyboardButtonCallback(text=second_btn,
                                           data=b'some_bytes'),

                ]
            ),
            KeyboardButtonRow(
                [
                    KeyboardButtonUrl(text=third_btn,
                                      url='https://google.com'),
                    KeyboardButtonCallback(text=third_btn,
                                           data=b'some_bytes'),

                ]
            ),
        ]
    )
    return inline_keyboard
