from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from redis.asyncio import Redis


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: int, period: int) -> None:
        super().__init__()
        self.limit = limit
        self.period = period

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Awaitable[Any] | None:

        redis_client: Redis = data['redis_client']
        i18n = data['i18n']
        user: User = data['event_from_user']
        user_id = user.id
        name = f"flooder{user_id}"
        attempts = await redis_client.incr(name=name, amount=1)
        await redis_client.expireat(name=name, when=datetime.now() + timedelta(seconds=self.period))
        if int(attempts) == self.limit:
            await event.bot.send_message(chat_id=user_id, text=i18n.get('throttling_text'))
            return
        elif int(attempts) > self.limit:
            return
        else:
            return await handler(event, data)
