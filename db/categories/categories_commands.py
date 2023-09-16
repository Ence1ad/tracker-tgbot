from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .categories_model import CategoriesModel


async def create_category(user_id: int, category_name: str,
                          db_session: async_sessionmaker[AsyncSession]) -> CategoriesModel:
    """
    Create a record in the categories db table and return the obj

    :param user_id: Telegram user id derived from call or message
    :param category_name: Category name written by user and checked with a validator
    :param db_session: AsyncSession derived from middleware
    :return: CategoriesModel object
    """
    async with db_session as session:
        async with session.begin():
            category_obj: CategoriesModel = \
                CategoriesModel(user_id=user_id, category_name=category_name)
            session.add(category_obj)
            await session.flush()

        await session.refresh(category_obj)
        return category_obj


async def select_categories(user_id: int, db_session: async_sessionmaker[AsyncSession]) -> list[tuple[int, str]]:
    """
    Select the records from the categories db table

    :param user_id: Telegram user id derived from call or message
    :param db_session: AsyncSession derived from middleware
    :return: list of sorted (by category_name) rows (category_id, category_name, user_id) from the categories table
    """
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
    """
    Update the category name in the categories table record

    :param user_id: Telegram user id derived from call or message
    :param category_id: Category id derived from the cache
    :param new_category_name: New category name, written by the user, required for updating
    :param db_session: AsyncSession derived from middleware
    :return: one if the update operation was successful, none if not
    """
    async with db_session as session:
        async with session.begin():
            udp_stmt = \
                update(CategoriesModel) \
                .where(CategoriesModel.user_id == user_id,
                       CategoriesModel.category_id == category_id) \
                .values(category_name=new_category_name)\
                .returning(CategoriesModel.category_id)

            res = await session.execute(udp_stmt)
            return res.scalar_one_or_none()


async def delete_category(user_id: int, category_id: int,
                          db_session: async_sessionmaker[AsyncSession]) -> int | None:
    """
    Delete the category record from the categories db table

    :param user_id: Telegram user_id derived from call or message
    :param category_id: Category id derived from the cache
    :param db_session: AsyncSession derived from middleware
    :return: one if the delete operation was successful, none if not
    """
    async with db_session as session:
        async with session.begin():
            del_stmt = \
                delete(CategoriesModel)\
                .where(CategoriesModel.user_id == user_id,
                       CategoriesModel.category_id == category_id)\
                .returning(CategoriesModel.category_id)

            returning = await session.execute(del_stmt)
            return returning.scalar_one_or_none()
