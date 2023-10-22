from contextlib import suppress
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from collections.abc import Callable,  Awaitable

from aiogram.utils.markdown import hide_link
from aiogram import BaseMiddleware
from aiogram.types import Update, User, ChatMemberRestricted, ChatMemberLeft,\
    ChatMemberBanned, ChatInviteLink
from fluentogram import TranslatorRunner
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cache.users_redis_manager import is_redis_sismember_user, redis_sadd_user_id
from config import settings
from db.operations.users_operations import create_user


async def _create_user_report_dir(user_id: int) -> None:
    """Create the user's report directory if it doesn't exist.

    :param user_id:  The user's ID.
    :return: None
    """
    user_report_dir: Path = Path(f'{settings.USER_REPORT_DIR}{user_id}')
    if not Path.is_dir(user_report_dir):
        Path.mkdir(user_report_dir)
    return None


class ChatMemberMiddleware(BaseMiddleware):
    """Middleware for handling chat member status and user registration.

    This middleware checks the status of users in a chat and manages user registration
    in Redis and the database. If a user is a bot, they are excluded.
    If a user's status in the chat is restricted, left, or banned, they are checked
    against the Redis set. If they are found in the Redis set, they are informed about
    chat re-entry. If a user is in the chat but not registered in Redis, they are added
    to Redis and the database.
    """

    def __init__(self) -> None:
        """Initialize the ChatMemberMiddleware.

        :return: None
        """
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any],
    ) -> Awaitable[Any] | None:
        """Handle incoming events based on user chat membership status.

        This method is called when a user interacts with the bot.
        It checks the user's status in the chat.
        If the user is a bot, they are excluded from further processing.
        If the user's status in the chat is restricted, left, or banned, the method
        checks whether the user is in the Redis set. If found, the user is informed
        about chat re-entry. If the user is in the chat but not registered in Redis,
        they are added to Redis and the database.

        :param handler: The next step in event processing.
        :param event: The incoming event.
        :param data: Additional data provided to the middleware.

        :return: The result of the handler function or None if
        certain conditions are met.
        """
        user: User = data['event_from_user']
        if user.is_bot:
            return None

        user_id: int = user.id
        redis_client: Redis = data['redis_client']
        db_session: AsyncSession = data['db_session']
        user_status = await event.bot.get_chat_member(settings.GROUP_ID, user_id)

        if isinstance(user_status,
                      (ChatMemberRestricted | ChatMemberLeft | ChatMemberBanned)):
            # While user in redis set, update will pass.
            # Then remove_user_handler will fire,
            # user will be removing from cache and db
            if await is_redis_sismember_user(user_id, redis_client):
                i18n: TranslatorRunner = data['i18n']
                expire_date: datetime = datetime.now() + timedelta(days=1)
                link: ChatInviteLink = await event.bot.create_chat_invite_link(
                    settings.GROUP_ID,
                    expire_date=expire_date,
                    member_limit=1
                )
                await event.bot.send_message(
                    user_id,
                    i18n.get('use_bot_text') + hide_link(link.invite_link)
                )

                return await handler(event, data)
            else:
                # If a user leaves the group but tries to trigger the bot,
                # just ignore it.
                return None
        else:
            is_user: bool | None = await is_redis_sismember_user(user_id, redis_client)
            # If the user is in the group and in the redis set,
            # then an update is passed.
            if is_user:
                return await handler(event, data)
            else:
                # Create user_report dir if not exists
                await _create_user_report_dir(user_id)
                # If the user is in the group but not in the redis,
                # add the user to the redis and the db
                first_name: str = user.first_name
                last_name: str | None = user.last_name
                username: str | None = user.username
                with suppress(IntegrityError):
                    await create_user(
                        user_id=user_id,
                        first_name=first_name,
                        last_name=last_name,
                        username=username,
                        db_session=db_session
                    )
                await redis_sadd_user_id(user_id, redis_client)
                return await handler(event, data)
