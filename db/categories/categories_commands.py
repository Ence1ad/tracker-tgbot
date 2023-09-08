from sqlalchemy import select, delete, update, Sequence, Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .categories_model import CategoriesModel


async def create_category(user_id: int, category_title: str,
                          db_session: async_sessionmaker[AsyncSession]) -> CategoriesModel:
    async with db_session as session:
        async with session.begin():
            category_obj: CategoriesModel = \
                CategoriesModel(user_id=user_id, category_name=category_title)
            session.add(category_obj)
            await session.flush()
        await session.refresh(category_obj)
        return category_obj


async def select_categories(user_id: int, db_session: async_sessionmaker[AsyncSession]) -> Sequence[Row[int, str]]:
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(CategoriesModel.category_id,
                       CategoriesModel.category_name)\
                .where(CategoriesModel.user_id == user_id)\
                .order_by(CategoriesModel.category_name)
            res = await session.execute(stmt)
            return res.fetchall()


async def update_category(user_id: int, category_id: int, new_category_name: str,
                          db_session: async_sessionmaker[AsyncSession]) -> None:
    async with db_session as session:
        async with session.begin():
            udp_stmt = \
                update(CategoriesModel) \
                .where(CategoriesModel.user_id == user_id,
                       CategoriesModel.category_id == category_id) \
                .values(category_name=new_category_name).returning(CategoriesModel.category_id)

            res = await session.execute(udp_stmt)
            return res.scalar_one_or_none()


async def delete_category(user_id: int, category_id: int,
                          db_session: async_sessionmaker[AsyncSession]) -> int | None:
    async with db_session as session:
        async with session.begin():
            del_stmt = \
                delete(CategoriesModel)\
                .where(CategoriesModel.user_id == user_id,
                       CategoriesModel.category_id == category_id).returning(CategoriesModel.category_id)

            returning = await session.execute(del_stmt)
            return returning.scalar_one_or_none()
