from sqlalchemy import select, delete, update

from ..categories.categories_model import ActionsCategories
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


async def get_user_actions(user_id: int, category_id: int):
    async with await create_async_session() as session:
        async with session.begin():
            stmt = select(Actions, ActionsCategories).join(ActionsCategories).where(Actions.user_id == user_id, Actions.category_id == category_id)
            res = await session.execute(stmt)
            await session.commit()
            return res.fetchall()


async def delete_action(user_id: int, action_id: int) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = delete(Actions).where(Actions.user_id == user_id,
                                         Actions.action_id == action_id)
            await session.execute(stmt)
            await session.commit()


async def update_action(user_id: int, action_id: int, new_action_name: int) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = update(Actions).where(Actions.user_id == user_id, Actions.action_id == action_id) \
                .values(action_name=new_action_name)
            await session.execute(stmt)
            await session.commit()
