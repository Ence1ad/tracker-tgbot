from telethon.tl.types import KeyboardButtonRow, ReplyInlineMarkup, KeyboardButtonUrl, KeyboardButtonCallback


def start_kb() -> ReplyInlineMarkup:
    inline_keyboard = ReplyInlineMarkup(
        [
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(text="Обо мне",
                                           data=b'some_bytes'),
                    KeyboardButtonCallback(text="Пройти тест",
                                           data=b'some_bytes'),

                ]
            ),
            KeyboardButtonRow(
                [
                    KeyboardButtonUrl(text="Мой сайт",
                                      url='https://google.com'),
                    KeyboardButtonCallback(text="Заказать курс",
                                           data=b'some_bytes'),

                ]
            ),
        ]
    )
    return inline_keyboard
