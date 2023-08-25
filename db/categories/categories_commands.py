from sqlalchemy import select, delete, ScalarResult, update

from ..db_session import create_async_session
from .categories_model import CategoriesModel


async def create_category(user_id, category_title: str) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            create_stmt: CategoriesModel = \
                CategoriesModel(category_name=category_title,
                                user_id=user_id)

            session.add(create_stmt)


async def select_categories(user_id: int) -> ScalarResult:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = \
                select(CategoriesModel.category_id,
                       CategoriesModel.category_name)\
                .where(CategoriesModel.user_id == user_id)\
                .order_by(CategoriesModel.category_name)

            return await session.execute(stmt)


async def update_category(user_id: int, category_id: int, new_category_name: str) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            udp_stmt = \
                update(CategoriesModel) \
                .where(CategoriesModel.user_id == user_id,
                       CategoriesModel.category_id == category_id) \
                .values(category_name=new_category_name)

            await session.execute(udp_stmt)


async def delete_category(user_id: int, category_id: int) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            del_stmt = \
                delete(CategoriesModel)\
                .where(CategoriesModel.user_id == user_id,
                       CategoriesModel.category_id == category_id)

            await session.execute(del_stmt)


async def category_exists(user_id: int, category_id: int) -> int | None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = \
                select(CategoriesModel.category_id)\
                .where(CategoriesModel.user_id == user_id,
                       CategoriesModel.category_id == category_id)

            res = await session.execute(stmt)
            return res.scalar_one_or_none()
