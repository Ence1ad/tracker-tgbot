from sqlalchemy import select

from ..db_session import create_async_session
from .user import UserModel, NewUser


async def create_user(user_obj: NewUser) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            new_user: UserModel = UserModel(user_id=user_obj.user_id,
                                            first_name=user_obj.first_name,
                                            last_name=user_obj.last_name,
                                            username=user_obj.username,
                                            phone=user_obj.phone)
            session.add(new_user)


async def check_user_in_db(user_id: int) -> str | None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = select(UserModel.user_id).where(UserModel.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalar()
