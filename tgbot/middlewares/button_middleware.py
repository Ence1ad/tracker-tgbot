from typing import Any
from collections.abc import Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update

from tgbot.keyboards.app_buttons import AppButtons


class ButtonsMiddleware(BaseMiddleware):
    def __init__(self, buttons: AppButtons) -> None:
        """Initialize the ButtonsMiddleware.

        :param buttons: The AppButtons instance providing predefined buttons.
        :type buttons: AppButtons

        This middleware is responsible for providing predefined button data to the
        Telegram bot, allowing easy access to various buttons for use in message replies
        and interactions.

        """
        super().__init__()
        self.buttons = buttons

    async def __call__(
            self,
            handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any],
    ) -> Awaitable[Any]:
        """Handle incoming events with button data provisioning.

        :param handler: The event handler function to be called.
        :type handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]]

        :param event: The incoming Telegram event.
        :type event: Update

        :param data: Data associated with the event.
        :type data: Dict[str, Any]

        :return: The result of the event handler.
        :rtype: Awaitable[Any]

        This method is called when an event is received by the Telegram bot.
        It associates the provided AppButtons instance with the event data, making
        predefined buttons accessible for use in messages and interactions.

        """
        data["buttons"] = self.buttons
        return await handler(event, data)
