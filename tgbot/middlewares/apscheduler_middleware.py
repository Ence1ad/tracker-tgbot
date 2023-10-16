from typing import Any
from collections.abc import Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from apscheduler_di import ContextSchedulerDecorator


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: ContextSchedulerDecorator) -> None:
        """Initialize the SchedulerMiddleware.

        :param scheduler: The APScheduler instance used for scheduling tasks.
        :type scheduler: ContextSchedulerDecorator

        This middleware is responsible for integrating an APScheduler instance into the
        Telegram bot. The APScheduler allows scheduling and executing tasks at specified
        intervals.

        """
        super().__init__()
        self.scheduler = scheduler

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Awaitable[Any]:
        """Handle incoming events with APScheduler integration.

        :param handler: The event handler function to be called.
        :type handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]]

        :param event: The incoming Telegram event.
        :type event: TelegramObject

        :param data: Data associated with the event.
        :type data: Dict[str, Any]

        :return: The result of the event handler.
        :rtype: Awaitable[Any]

        This method is called when an event is received by the Telegram bot.
        It associates the provided APScheduler instance with the event data, allowing
        for scheduling and executing tasks at specified intervals using APScheduler.

        """
        data["apscheduler"] = self.scheduler
        return await handler(event, data)
