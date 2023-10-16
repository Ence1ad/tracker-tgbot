from typing import Any
from collections.abc import Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update, User
from fluentogram import TranslatorHub
from redis.asyncio import Redis
from cache.language_redis_manager import redis_hget_lang
from tgbot.localization.localize import Translator


class TranslatorRunnerMiddleware(BaseMiddleware):
    """Middleware for language translation using Fluentogram.

    This middleware is designed to handle language translation for your bot
    using the Fluentogram library. It allows you to dynamically translate messages
    based on the user's preferred language, which is stored in Redis.

    :param translator: Translator: An instance of the Translator class
    that handles bot localization.
    """

    def __init__(self, translator: Translator) -> None:
        """Initialize the TranslatorRunnerMiddleware.

        This method is called when creating an instance of the middleware.
        It sets up the middleware with the provided `translator` for language
        translation.

        :param translator: Translator: An instance of the Translator class that
        handles bot localization.
        """
        super().__init__()
        self.translator = translator
        self.lang = translator.global_lang

    async def __call__(
            self,
            handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ) -> Awaitable[Any]:
        """Process the middleware for translating messages.

        This method is automatically called by Aiogram for each incoming update.
        It checks the user's preferred language stored in Redis, and based on that
        language, it sets up a TranslatorRunner for translating messages.

        :param handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]]:
         The handler for the next middleware or the final handler.
        :param event: Update: The incoming update event.
        :param data: Dict[str, Any]: Additional data associated with the update.
        :return: Awaitable[Any]: The result of calling the next middleware or handler.
        """
        redis_client: Redis = data.get('redis_client')
        user: User = data['event_from_user']
        user_id = user.id

        self.lang = await redis_hget_lang(user_id, redis_client, local=self.lang)
        hub: TranslatorHub = self.translator.t_hub
        data['i18n'] = hub.get_translator_by_locale(self.lang)
        return await handler(event, data)
