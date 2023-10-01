from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Awaitable

from aiogram.utils.markdown import hide_link
from aiogram import BaseMiddleware
from aiogram.types import Update, User, ChatMemberRestricted, ChatMemberLeft, ChatMemberBanned
from redis.asyncio import Redis

from cache.redis_schedule_command import is_redis_sismember_user
from config import settings


class ChatMemberMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Awaitable[Any] | None:

        """
        The __call__ function is the function that will be called when a user sends a message to the bot.
        It will check that the user is still a chat participant, and if not, it will send message with the chat link

        :param self: Access the class attributes
        :param handler: Callable[[Update: Pass the update object to the handler
        :param Dict[str: Pass the data to the handler
        :param Any]]: Pass the handler function to the decorator
        :param Awaitable[Any]]: Return a value that can be awaited
        :param event: Update: Get the update object
        :param data: Dict[str: Pass the data from the dispatcher to this middleware
        :param Any]: Pass the data to the next handler
        :param : Pass the function that will be called after the filter
        :return: The result of the handler function
        """
        user: User = data['event_from_user']
        if user.is_bot:
            return

        user_id = user.id
        redis_client: Redis = data['redis_client']

        user_status = await event.bot.get_chat_member(settings.GROUP_ID, user_id)

        if isinstance(user_status, (ChatMemberRestricted | ChatMemberLeft | ChatMemberBanned)):
            # while user in redis set, update will pass. Then remove_user_handler will fire,
            # user will be removing from cache and db
            if await is_redis_sismember_user(user_id, redis_client):
                i18n = data['i18n']
                expire_date = datetime.now() + timedelta(days=1)
                link = await event.bot.create_chat_invite_link(settings.GROUP_ID, expire_date=expire_date,
                                                               member_limit=1)
                await event.bot.send_message(user_id, i18n.get('use_bot_text') + hide_link(link.invite_link))

                return await handler(event, data)
            else:
                return
        else:
            return await handler(event, data)
