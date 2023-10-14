from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user_model import UserModel


async def create_user(user_id: int, first_name: str, last_name: str | None,
                      username: str | None, db_session: AsyncSession) -> UserModel:
    """
    Create a new user record in the database and return the corresponding UserModel object.

    :param user_id: int: The Telegram user ID associated with the user.
    :param first_name: str: The first name of the user.
    :param last_name: str: The last name of the user.
    :param username: str: The username of the user.
    :param db_session: AsyncSession: The asynchronous database session used for the operation.

    :return: UserModel: An instance of the UserModel class representing the created user.
    """
    async with db_session as session:
        async with session.begin():
            user_obj: UserModel = \
                UserModel(user_id=user_id, first_name=first_name, last_name=last_name, username=username,)
            session.add(user_obj)
            await session.flush()
        await session.refresh(user_obj)
        return user_obj


async def delete_user(user_id: int, db_session: AsyncSession) -> int | None:
    """
    Delete a user record from the database by their user_id.

    :param user_id: int: The user_id of the user to be deleted.
    :param db_session: AsyncSession: The asynchronous database session.

    :return: int | None: The user_id of the deleted user, or None if the user doesn't exist.
    """
    async with db_session as session:
        async with session.begin():
            del_stmt = \
                delete(UserModel)\
                .where(UserModel.user_id == user_id)\
                .returning(UserModel.user_id)

            returning = await session.execute(del_stmt)
        return returning.scalar_one_or_none()
