from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.engine.row import Row
from db.models.action_model import ActionsModel


async def create_actions(user_id: int, action_name: str, category_id: int,
                         db_session: async_sessionmaker[AsyncSession]) -> ActionsModel:
    """
    The create_actions function creates a new action in the database.

    :param user_id: int: Identify the user who is creating the action
    :param action_name: str: Create the action name
    :param category_id: int: Create a new action
    :param db_session: async_sessionmaker[AsyncSession]: Pass the database session to the function
    :return: The ActionsModel object
    """
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
                                  ) -> list[Row[int, str]]:

    """
    The select_category_actions function is used to select all actions associated with a given category.
        The function takes in the user_id and category_id of the user and category respectively, as well as an
        async session object. It then uses these parameters to query the database for all actions that are associated
        with this particular user's account and this particular category. The results are returned in a list of rows
        (tuples), where each row contains two elements: (action_id, action_name). If no results are found, empty list
         will be returned instead.

    :param user_id: int: Identify the user
    :param category_id: int: Filter the actions by category_id
    :param db_session: async_sessionmaker[AsyncSession]: Pass the database session to the function
    :return: A list of rows(tuples) with the action_id and action_name
    """
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(ActionsModel.action_id,
                       ActionsModel.action_name)\
                .where(ActionsModel.user_id == user_id,
                       ActionsModel.category_id == category_id)\
                .order_by(ActionsModel.action_name)

            res = await session.execute(stmt)
            return res.fetchall()


async def update_action_name(user_id: int, action_id: int, new_action_name: str,
                             db_session: async_sessionmaker[AsyncSession]) -> int | None:

    """
    The update_action_name function updates the action_name of an existing action.

    :param user_id: int: Identify the user who is updating an action
    :param action_id: int: Identify the action to be updated
    :param new_action_name: str: Pass in the new action name
    :param db_session: async_sessionmaker[AsyncSession]: Pass the database session to the function
    :return: one if the update row was successful, none if not
    """
    async with db_session as session:
        async with session.begin():
            udp_stmt = \
                update(ActionsModel)\
                .where(ActionsModel.user_id == user_id,
                       ActionsModel.action_id == action_id) \
                .values(action_name=new_action_name)\
                .returning(ActionsModel.action_id)

            returning = await session.execute(udp_stmt)
            return returning.scalar_one_or_none()


async def delete_action(user_id: int, action_id: int, db_session: async_sessionmaker[AsyncSession]) -> int | None:
    """
    The delete_action function deletes an action from the database.

    :param user_id: int: Identify the user who is deleting an action
    :param action_id: int: Specify the action_id of the action to be deleted
    :param db_session: async_sessionmaker[AsyncSession]: Pass the database session to the function
    :return: one if the deleted action or none if no action was deleted
    """
    async with db_session as session:
        async with session.begin():
            del_stmt = \
                delete(ActionsModel)\
                .where(ActionsModel.user_id == user_id,
                       ActionsModel.action_id == action_id)\
                .returning(ActionsModel.action_id)

            returning = await session.execute(del_stmt)
            return returning.scalar_one_or_none()
