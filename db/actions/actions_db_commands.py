from sqlalchemy import select, delete, update, Result, func

from ..categories.categories_model import CategoriesModel
from ..db_session import create_async_session
from .actions_models import ActionsModel


async def create_actions(user_id: int, action_name: str, category_id: int) -> None:
    # TODO необходима проверка существует ли категория перед созданием действия
    async with await create_async_session() as session:
        async with session.begin():
            create_stmt: ActionsModel = \
                ActionsModel(action_name=action_name,
                             category_id=category_id,
                             user_id=user_id)
            session.add(create_stmt)


async def select_category_actions(user_id: int, category_id: int) -> Result:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = \
                select(ActionsModel.action_id,
                       ActionsModel.action_name,
                       CategoriesModel.category_name)\
                .join(CategoriesModel) \
                .where(ActionsModel.user_id == user_id,
                       ActionsModel.category_id == category_id)\
                .order_by(ActionsModel.action_name)

            return await session.execute(stmt)


async def select_actions_for_tracker(user_id: int, category_name: str):
    async with await create_async_session() as session:
        async with session.begin():
            stmt = \
                select(ActionsModel.action_id,
                       ActionsModel.action_name,
                       CategoriesModel.category_name)\
                .join(CategoriesModel) \
                .where(ActionsModel.user_id == user_id,
                       CategoriesModel.category_name == category_name)

            return await session.execute(stmt)


async def delete_action(user_id: int, action_id: int) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            del_stmt = \
                delete(ActionsModel)\
                .where(ActionsModel.user_id == user_id,
                       ActionsModel.action_id == action_id)

            await session.execute(del_stmt)


async def update_action(user_id: int, action_id: int, new_action_name: str) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            udp_stmt = \
                update(ActionsModel)\
                .where(ActionsModel.user_id == user_id,
                       ActionsModel.action_id == action_id) \
                .values(action_name=new_action_name)

            await session.execute(udp_stmt)


async def select_action_count(user_id: int, category_id: int) -> int | None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = \
                select(func.count(ActionsModel.action_id))\
                .where(ActionsModel.user_id == user_id,
                       ActionsModel.category_id == category_id)

            action_cnt = await session.execute(stmt)
            return action_cnt.scalar_one_or_none()


async def action_exists(user_id: int, action_id: int) -> int | None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = \
                select(ActionsModel.action_id)\
                .where(ActionsModel.user_id == user_id,
                       ActionsModel.action_id == action_id)

            res = await session.execute(stmt)
            return res.scalar_one_or_none()
