from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update
from redis.asyncio import Redis


class CacheMiddleware(BaseMiddleware):
    """
    Initialize the CacheMiddleware.

    :param redis_client: The Redis cache client used for caching.
    :type redis_client: Redis

    This middleware is responsible for managing the Redis cache client, allowing for caching and
    retrieval of data during bot operation.
    """
    def __init__(self, redis_client: Redis) -> None:
        super().__init__()
        self.redis_client = redis_client

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Awaitable[Any]:
        """
        Handle incoming events with Redis cache client management.

        :param handler: The event handler function to be called.
        :type handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]]

        :param event: The incoming CallbackQuery event.
        :type event: CallbackQuery

        :param data: Data associated with the event.
        :type data: Dict[str, Any]

        :return: The result of the event handler.
        :rtype: Awaitable[Any]

        This method is called when an event is received by the Telegram bot. It associates the provided
        Redis cache client with the event data, allowing for caching and retrieval of data during event
        processing. Control is then passed to the provided event handler.
        """
        data["redis_client"] = self.redis_client
        return await handler(event, data)
