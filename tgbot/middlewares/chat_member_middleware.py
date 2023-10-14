from contextlib import suppress
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Awaitable

from aiogram.utils.markdown import hide_link
from aiogram import BaseMiddleware
from aiogram.types import Update, User, ChatMemberRestricted, ChatMemberLeft, ChatMemberBanned
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from cache.users_redis_manager import is_redis_sismember_user, redis_sadd_user_id
from config import settings
from db.operations.users_operations import create_user


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
        db_session: async_sessionmaker[AsyncSession] = data['db_session']
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
                # If a user leaves the group but tries to trigger the bot, just ignore it.
                return
        else:
            is_user = await is_redis_sismember_user(user_id, redis_client)
            # If the user is in the group and in the redis set, then an update is passed.
            if is_user:
                return await handler(event, data)
            else:
                # If the user is in the group but not in the redis, add the user to the redis and the db
                first_name = user.first_name
                last_name = user.last_name
                username = user.username
                with suppress(IntegrityError):
                    await create_user(user_id=user_id, first_name=first_name, last_name=last_name, username=username,
                                      db_session=db_session)
                await redis_sadd_user_id(user_id, redis_client)
                return await handler(event, data)
