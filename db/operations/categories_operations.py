from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.engine.row import Row

from db.models.category_model import CategoriesModel
from db import ActionsModel


async def create_category(user_id: int, category_name: str,
                          db_session: async_sessionmaker[AsyncSession]) -> CategoriesModel:
    """
    The create_category function creates a new category for the user.

    :param user_id: int: Identify the user that created the category
    :param category_name: str: Create a new category
    :param db_session: async_sessionmaker[AsyncSession]: Pass the database session to the function
    :return: A CategoriesModel object
    """
    async with db_session as session:
        async with session.begin():
            category_obj: CategoriesModel = \
                CategoriesModel(user_id=user_id, category_name=category_name)
            session.add(category_obj)
            await session.flush()

        await session.refresh(category_obj)
        return category_obj


async def select_categories(user_id: int, db_session: async_sessionmaker[AsyncSession]) -> list[Row[int, str]]:

    """
    The select_categories function returns a list of rows(tuples) containing the category_id, category_name and
    count of actions for each category of all categories belonging to the user with id = user_id.
    If no results are found, empty list will be returned instead.

    :param user_id: int: Select the categories for a specific user
    :param db_session: async_sessionmaker[AsyncSession]: Pass the database session to the function
    :return: A list of rows(tuples) with the category_id, category_name and actions count  or empty list
    """
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(CategoriesModel.category_id,
                       CategoriesModel.category_name,
                       func.count(ActionsModel.action_id))\
                .outerjoin(ActionsModel)\
                .where(CategoriesModel.user_id == user_id)\
                .group_by(CategoriesModel.category_id, CategoriesModel.category_name)\
                .order_by(CategoriesModel.category_name)

            res = await session.execute(stmt)
            return res.fetchall()


async def select_categories_with_actions(user_id: int, db_session: async_sessionmaker[AsyncSession]
                                         ) -> list[Row[int, str]]:

    """
    The select_categories_with_actions function returns a list of tuples containing the category_id,
    category_name and count of actions for each category. The function is used to populate the categories
    dropdown menu in the main page.

    :param user_id: int: Identify the user
    :param db_session: async_sessionmaker[AsyncSession]: Create a new session to the database
    :return: A list of tuples
    """
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(CategoriesModel.category_id,
                       CategoriesModel.category_name,
                       func.count(ActionsModel.action_id))\
                .outerjoin(ActionsModel)\
                .where(CategoriesModel.user_id == user_id,
                       ActionsModel.action_id.is_not(None)) \
                .group_by(CategoriesModel.category_id, CategoriesModel.category_name) \
                .order_by(CategoriesModel.category_name)

            res = await session.execute(stmt)
            return res.fetchall()


async def select_category_id(user_id: int, category_name: str, db_session: async_sessionmaker[AsyncSession]
                             ) -> int | None:
    """
    The select_category_id function takes in a user_id, category_name, and db_session.
    It then uses the db session to query the database for a category id that matches both
    the user id and category name provided. If it finds one, it returns that value as an int;
    otherwise it returns None.

    :param user_id: int: Identify the user who owns the category
    :param category_name: str: Select the category_id of a specific category
    :param db_session: async_sessionmaker[AsyncSession]: Make a connection to the database
    :return: The id of the category with the specified name
    """
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(CategoriesModel.category_id)\
                .where(CategoriesModel.user_id == user_id,
                       CategoriesModel.category_name == category_name)

            res = await session.execute(stmt)
            return res.scalar_one_or_none()


async def update_category(user_id: int, category_id: int, new_category_name: str,
                          db_session: async_sessionmaker[AsyncSession]) -> None:
    """
    The update_category function updates the category name of a given user's category.

    :param user_id: int: Identify the user
    :param category_id: int: Identify the category to be updated
    :param new_category_name: str: Update the category name
    :param db_session: async_sessionmaker[AsyncSession]: Pass the database session to the function
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
    The delete_category function deletes of a given user's category from the database.

    :param user_id: int: Identify the user that is deleting a category
    :param category_id: int: Specify the category to delete
    :param db_session: async_sessionmaker[AsyncSession]: Pass the database session to the function
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
