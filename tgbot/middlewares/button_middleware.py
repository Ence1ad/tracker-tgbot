from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from tgbot.keyboards.app_buttons import AppButtons


class ButtonsMiddleware(BaseMiddleware):
    def __init__(self, buttons: AppButtons) -> None:
        super().__init__()
        self.buttons = buttons

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any],
    ) -> Awaitable[Any]:

        data["buttons"] = self.buttons
        return await handler(event, data)
