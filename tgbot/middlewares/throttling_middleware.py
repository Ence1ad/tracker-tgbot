from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorRunner
from redis.asyncio import Redis


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: int, period: int) -> None:
        """
        Initialize the ThrottlingMiddleware.

        :param limit: The maximum number of allowed requests within the specified period.
        :type limit: int

        :param period: The time period (in seconds) during which the request limit applies.
        :type period: int

        This middleware is responsible for managing request throttling by limiting the number of
        incoming requests from users within a specified time period.

        """
        super().__init__()
        self.limit = limit
        self.period = period

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Awaitable[Any] | None:
        """
        Handle incoming events with request throttling.

        :param handler: The event handler function to be called.
        :type handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]]

        :param event: The incoming Telegram event.
        :type event: TelegramObject

        :param data: Data associated with the event.
        :type data: Dict[str, Any]

        :return: The result of the event handler or None if the request limit is exceeded.
        :rtype: Awaitable[Any] | None

        This method is called when an event is received by the Telegram bot. It tracks the number of
        incoming requests from a user within the specified time period and enforces request throttling.
        If the request limit is exceeded, a message is sent to the user, and the event handler is not
        invoked.

        """
        redis_client: Redis = data['redis_client']
        i18n: TranslatorRunner = data['i18n']
        user: User = data['event_from_user']
        user_id: int = user.id
        name: str = f"flooder{user_id}"
        attempts: bytes = await redis_client.incr(name=name, amount=1)
        await redis_client.expireat(name=name, when=datetime.now() + timedelta(seconds=self.period))
        if int(attempts) == self.limit:
            await event.bot.send_message(chat_id=user_id, text=i18n.get('throttling_text'))
            return None
        elif int(attempts) > self.limit:
            return None
        else:
            return await handler(event, data)
