from contextlib import suppress

from aiogram import Bot
from aiogram.types import ChatMemberAdministrator
from sqlalchemy.exc import IntegrityError

from cache.user_redis_utils import redis_sadd_user_id
from db.users.users_commands import create_user


async def add_admin(admin_id, db_session, redis_client):
    db_session = db_session()
    with suppress(IntegrityError):
        await create_user(user_id=admin_id, first_name='', last_name='', username='', db_session=db_session)
    await redis_sadd_user_id(user_id=admin_id, redis_client=redis_client)


async def is_bot_admin(bot: Bot, chat_id: int):
    chat_member_info = await bot.get_chat_member(chat_id=chat_id, user_id=bot.id)
    if not isinstance(chat_member_info, ChatMemberAdministrator):
        raise PermissionError("Bot is not an administrator")
    # if not chat_member_info.can_restrict_members or not chat_member_info.can_delete_messages:
    #     raise PermissionError("Bot needs 'restrict participants' and 'delete messages' permissions to work properly")
