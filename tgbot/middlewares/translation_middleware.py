from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update

from fluentogram import TranslatorHub, TranslatorRunner
from redis.asyncio import Redis

from cache.redis_language_commands import redis_hget_lang
from tgbot.localization.localize import Translator


class TranslatorRunnerMiddleware(BaseMiddleware):
    def __init__(self, translator: Translator) -> None:
        super().__init__()
        self.translator = translator
        self.lang = translator.global_lang

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Awaitable[Any]:

        redis_client: Redis = data.get('redis_client')
        if event.message is not None:
            user_id: int = event.message.from_user.id
            self.lang = await redis_hget_lang(user_id, redis_client, local=self.lang)
        elif event.callback_query is not None:
            user_id: int = event.callback_query.from_user.id
            self.lang = await redis_hget_lang(user_id, redis_client, local=self.lang)

        hub: TranslatorHub = self.translator.t_hub
        data['i18n']: TranslatorRunner = hub.get_translator_by_locale(self.lang)
        return await handler(event, data)
