from sqlalchemy import select, delete, ScalarResult, update

from ..db_session import create_async_session
from .categories_model import ActionsCategories


async def create_category(user_id, category_title: str) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            new_category: ActionsCategories = ActionsCategories(
                category_name=category_title,
                user_id=user_id)
            session.add(new_category)
            await session.commit()


async def get_categories(user_id: int) -> ScalarResult:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = select(ActionsCategories).where(ActionsCategories.user_id == user_id)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalars()


async def update_category(user_id: int, category_id: int, new_category_name: str) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = update(ActionsCategories) \
                .where(ActionsCategories.user_id == user_id, ActionsCategories.category_id == category_id) \
                .values(category_name=new_category_name)
            await session.execute(stmt)
            await session.commit()


async def delete_category(user_id: int, category_id: int) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = delete(ActionsCategories).where(ActionsCategories.user_id == user_id,
                                                   ActionsCategories.category_id == category_id)
            await session.execute(stmt)
            await session.commit()
