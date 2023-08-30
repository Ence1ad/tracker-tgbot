from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .user import UserModel, NewUser


async def create_user(user_obj: NewUser, db_session: AsyncSession) -> None:
    async with db_session as session:
        async with session.begin():
            create_stmt: UserModel = \
                UserModel(user_id=user_obj.user_id,
                          first_name=user_obj.first_name,
                          last_name=user_obj.last_name,
                          username=user_obj.username,
                          phone=user_obj.phone)
            session.add(create_stmt)


async def check_user_in_db(user_id: int, db_session: AsyncSession) -> str | None:
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(UserModel.user_id)\
                .where(UserModel.user_id == user_id)

            result = await session.execute(stmt)
            return result.scalar()
