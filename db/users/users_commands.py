from sqlalchemy.ext.asyncio import AsyncSession

from .user_model import UserModel


async def create_user(user_id: int,
                      first_name: str,
                      last_name: str,
                      username: str,
                      db_session: AsyncSession
                      ) -> UserModel:

    async with db_session as session:
        async with session.begin():
            user_obj: UserModel = \
                UserModel(user_id=user_id,
                          first_name=first_name,
                          last_name=last_name,
                          username=username,
                          )
            session.add(user_obj)
            await session.flush()
        await session.refresh(user_obj)
        return user_obj
