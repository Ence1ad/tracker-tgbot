from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update

from fluentogram import TranslatorHub, TranslatorRunner
from redis.asyncio import Redis

from cache.redis_language_commands import redis_hget_lang
from config import settings


class TranslatorRunnerMiddleware(BaseMiddleware):
    def __init__(self, translator: TranslatorHub) -> None:
        super().__init__()
        self.translator = translator

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        # If you don't use __init__
        # hub: TranslatorHub = data.get('_translator_hub')
        # There you can ask your database for locale
        redis_client: Redis = data.get('redis_client')
        if event.message is not None:
            user_id: int = event.message.from_user.id
            local = await redis_hget_lang(user_id, redis_client)
        elif event.callback_query is not None:
            user_id: int = event.callback_query.from_user.id
            local = await redis_hget_lang(user_id, redis_client)
        else:
            local = settings.EN_LANG_CODE
        hub: TranslatorHub = self.translator
        data['i18n']: TranslatorRunner = hub.get_translator_by_locale(local)
        return await handler(event, data)

