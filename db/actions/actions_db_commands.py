from sqlalchemy import select, delete, ScalarResult, update

from ..db_session import create_async_session
from .actions_models import Actions


async def create_actions(user_id, action_name, category_id: str) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            create_action: Actions = Actions(action_name=action_name,
                                             category_id=category_id,
                                             user_id=user_id
                                             )
            session.add(create_action)
            await session.commit()


async def get_user_actions(user_id, category_id) -> ScalarResult:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = select(Actions).where(Actions.user_id == user_id, Actions.category_id == category_id)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalars()


async def delete_action(user_id, action_id) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = delete(Actions).where(Actions.user_id == user_id,
                                         Actions.action_id == action_id)
            await session.execute(stmt)
            await session.commit()


async def update_action(user_id, action_id, new_action_name) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = update(Actions).where(Actions.user_id == user_id, Actions.action_id == action_id) \
                .values(action_name=new_action_name)
            await session.execute(stmt)
            await session.commit()
