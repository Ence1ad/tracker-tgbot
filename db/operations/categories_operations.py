from sqlalchemy import select, delete, update, func, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.category_model import CategoryModel
from db import ActionModel


async def create_category(user_id: int, category_name: str,
                          db_session: AsyncSession) -> CategoryModel:
    """Create a new category for a user.

    :param user_id: The user's ID.
    :param category_name: The name of the category.
    :param db_session: The asynchronous database session.

    :return: A CategoryModel object representing the created category.
    """
    async with db_session as session:
        async with session.begin():
            category_obj: CategoryModel = \
                CategoryModel(user_id=user_id, category_name=category_name)
            session.add(category_obj)
            await session.flush()

        await session.refresh(category_obj)
        return category_obj


async def select_categories(user_id: int, db_session: AsyncSession
                            ) -> Sequence:
    """Retrieve categories for a user, including the count of associated actions.

    :param user_id: The user's ID.
    :param db_session: The asynchronous database session.

    :return: A sequence of Row objects containing category information.
    """
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(CategoryModel.category_id,
                       CategoryModel.category_name,
                       func.count(ActionModel.action_id))\
                .outerjoin(ActionModel)\
                .where(CategoryModel.user_id == user_id)\
                .group_by(CategoryModel.category_id, CategoryModel.category_name)\
                .order_by(CategoryModel.category_name)

            res = await session.execute(stmt)
            return res.fetchall()


async def select_categories_with_actions(user_id: int, db_session: AsyncSession
                                         ) -> Sequence:
    """Retrieve categories with associated actions for a user.

    :param user_id: The user's ID.
    :param db_session: The asynchronous database session.

    :return: A sequence of Row objects containing category information.
    """
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(CategoryModel.category_id,
                       CategoryModel.category_name,
                       func.count(ActionModel.action_id))\
                .outerjoin(ActionModel)\
                .where(CategoryModel.user_id == user_id,
                       ActionModel.action_id.is_not(None)) \
                .group_by(CategoryModel.category_id, CategoryModel.category_name) \
                .order_by(CategoryModel.category_name)

            res = await session.execute(stmt)
            return res.fetchall()


async def select_category_id(user_id: int, category_name: str, db_session: AsyncSession
                             ) -> int | None:
    """Retrieve the ID of a category by its name for a user.

    :param user_id: The user's ID.
    :param category_name: The name of the category.
    :param db_session: The asynchronous database session.

    :return: The category ID or None if not found.
    """
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(CategoryModel.category_id)\
                .where(CategoryModel.user_id == user_id,
                       CategoryModel.category_name == category_name)

            res = await session.execute(stmt)
            return res.scalar_one_or_none()


async def update_category(user_id: int, category_id: int, new_category_name: str,
                          db_session: AsyncSession) -> None:
    """Update the name of a user's category.

    :param user_id: The user's ID.
    :param category_id: The ID of the category to update.
    :param new_category_name: The new name for the category.
    :param db_session: The asynchronous database session.
    """
    async with db_session as session:
        async with session.begin():
            udp_stmt = \
                update(CategoryModel) \
                .where(CategoryModel.user_id == user_id,
                       CategoryModel.category_id == category_id) \
                .values(category_name=new_category_name)\
                .returning(CategoryModel.category_id)

            res = await session.execute(udp_stmt)
            return res.scalar_one_or_none()


async def delete_category(user_id: int, category_id: int,
                          db_session: AsyncSession) -> int | None:
    """Delete a category for a user.

    :param user_id: The user's ID.
    :param category_id: The ID of the category to delete.
    :param db_session: The asynchronous database session.

    :return: The ID of the deleted category or None if not found.
    """
    async with db_session as session:
        async with session.begin():
            del_stmt = \
                delete(CategoryModel)\
                .where(CategoryModel.user_id == user_id,
                       CategoryModel.category_id == category_id)\
                .returning(CategoryModel.category_id)

            returning = await session.execute(del_stmt)
            return returning.scalar_one_or_none()
