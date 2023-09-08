from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from redis.asyncio import Redis


class CacheMiddleware(BaseMiddleware):
    def __init__(self, redis_client: Redis) -> None:
        super().__init__()
        self.redis_client = redis_client

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:

        data["redis_client"] = self.redis_client
        return await handler(event, data)
