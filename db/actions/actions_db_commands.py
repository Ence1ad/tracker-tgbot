from sqlalchemy import select, delete, update, Sequence, Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..categories.categories_model import CategoriesModel
from .actions_models import ActionsModel


async def create_actions(user_id: int, action_name: str, category_id: int,
                         db_session: async_sessionmaker[AsyncSession]) -> ActionsModel:
    async with db_session as session:
        async with session.begin():
            action_obj: ActionsModel = \
                ActionsModel(action_name=action_name,
                             category_id=category_id,
                             user_id=user_id)
            session.add(action_obj)
            await session.flush()
        await session.refresh(action_obj)
        return action_obj


async def select_category_actions(user_id: int, category_id: int, db_session: async_sessionmaker[AsyncSession]
                                  ) -> Sequence[Row[int, str]]:
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(ActionsModel.action_id,
                       ActionsModel.action_name,
                       CategoriesModel.category_id,
                       CategoriesModel.category_name)\
                .join(CategoriesModel) \
                .where(ActionsModel.user_id == user_id,
                       ActionsModel.category_id == category_id)\
                .order_by(ActionsModel.action_name)
            res = await session.execute(stmt)
            return res.fetchall()


async def delete_action(user_id: int, action_id: int, db_session: async_sessionmaker[AsyncSession]) -> int | None:
    async with db_session as session:
        async with session.begin():
            del_stmt = \
                delete(ActionsModel)\
                .where(ActionsModel.user_id == user_id,
                       ActionsModel.action_id == action_id).returning(ActionsModel.action_id)

            returning = await session.execute(del_stmt)
            return returning.scalar_one_or_none()


async def update_action(user_id: int, action_id: int, new_action_name: str,
                        db_session: async_sessionmaker[AsyncSession]) -> int | None:
    async with db_session as session:
        async with session.begin():
            udp_stmt = \
                update(ActionsModel)\
                .where(ActionsModel.user_id == user_id,
                       ActionsModel.action_id == action_id) \
                .values(action_name=new_action_name).returning(ActionsModel.action_id)

            returning = await session.execute(udp_stmt)
            return returning.scalar_one_or_none()


# async def select_action_count(user_id: int, category_id: int,
#                               db_session: async_sessionmaker[AsyncSession]) -> int | None:
#     async with db_session as session:
#         async with session.begin():
#             stmt = \
#                 select(func.count(ActionsModel.action_id))\
#                 .where(ActionsModel.user_id == user_id,
#                        ActionsModel.category_id == category_id)
#
#             action_cnt = await session.execute(stmt)
#             return action_cnt.scalar_one_or_none()
