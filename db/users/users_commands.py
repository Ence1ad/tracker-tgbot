from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .user_model import UserModel


async def create_user(user_id: int, first_name: str, last_name: str, username: str,
                      db_session: async_sessionmaker[AsyncSession]) -> UserModel:
    """
    Create a record in the users db table and return the obj

    :param user_id: Telegram user id derived from call or message
    :param first_name: Telegram first name derived from call or message
    :param last_name: Telegram last name derived from call or message
    :param username: Telegram username derived from call or message
    :param db_session:
    :return: UserModel object
    """
    async with db_session as session:
        async with session.begin():
            user_obj: UserModel = \
                UserModel(user_id=user_id, first_name=first_name, last_name=last_name, username=username,)
            session.add(user_obj)
            await session.flush()
        await session.refresh(user_obj)
        return user_obj
