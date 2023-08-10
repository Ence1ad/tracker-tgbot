from sqlalchemy import select, delete

from ..db_session import create_async_session
from .categories import ActionsCategories


async def create_category(user_id, category_title: str) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            new_category: ActionsCategories = ActionsCategories(
                category_name=category_title,
                user_id=user_id)
            session.add(new_category)


async def get_categories(user_id) -> list:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = select(ActionsCategories.category_name).where(ActionsCategories.user_id == user_id)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalars()

async def update_category() -> None:
    pass

async def delete_category(user_id, category_name) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = delete(ActionsCategories).where(ActionsCategories.user_id == user_id,
                                                   ActionsCategories.category_name == category_name)
            res = await session.execute(stmt)
            await session.commit()
