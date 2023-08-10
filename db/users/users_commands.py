from sqlalchemy import select

from ..db_session import create_async_session
from .user import SAUser, NewUser


async def create_user(user_obj: NewUser) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            new_user: SAUser = SAUser(user_id=user_obj.user_id,
                                      first_name=user_obj.first_name,
                                      last_name=user_obj.last_name,
                                      username=user_obj.username,
                                      phone=user_obj.phone)
            session.add(new_user)


async def check_user_in_db(sender_id: int) -> str | None:
    async with await create_async_session() as session:
        stmt = select(SAUser.user_id).where(SAUser.user_id == sender_id)
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar()
