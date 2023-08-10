from telethon.tl.types import KeyboardButtonRow, ReplyInlineMarkup, KeyboardButtonCallback
from tgbot.buttons_names import actions_btn, categories_btn, reports_btn, settings_btn


async def start_kb() -> ReplyInlineMarkup:
    reply_markup = ReplyInlineMarkup(
        [
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(text=actions_btn,
                                           data=b'some_bytes'),
                    KeyboardButtonCallback(text=categories_btn,
                                           data=b'categories_btn'),

                ]
            ),
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(text=reports_btn,
                                           data=b'reports_btn'),
                    KeyboardButtonCallback(text=settings_btn,
                                           data=b'some_bytes'),

                ]
            ),
        ]
    )
    return reply_markup
