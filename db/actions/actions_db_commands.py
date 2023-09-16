from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..categories.categories_model import CategoriesModel
from .actions_models import ActionsModel


async def create_actions(user_id: int, action_name: str, category_id: int,
                         db_session: async_sessionmaker[AsyncSession]) -> ActionsModel:
    """
    Create a record in the actions db table and return the obj

    :param user_id: Telegram user id derived from call or message
    :param action_name: Action name written by user
    :param category_id: Category id derived from the FSM context state
    :param db_session: AsyncSession derived from middleware
    :return: ActionsModel object
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
                                  ) -> list[tuple[int, str]]:
    """
    Select the records from the actions db table

    :param user_id: Telegram user id derived from call or message
    :param category_id: Category id derived from the cache
    :param db_session: AsyncSession derived from middleware
    :return: list of sorted (by action_name) rows (action_id, action_name,
     category_id, category_name from the actions table
    """
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


async def update_action_name(user_id: int, action_id: int, new_action_name: str,
                             db_session: async_sessionmaker[AsyncSession]) -> int | None:
    """
    Update the action name in the actions table record

    :param user_id: Telegram user id derived from call or message
    :param action_id: Action id derived from the cache
    :param new_action_name: New action name, written by the user, required for updating
    :param db_session: AsyncSession derived from middleware
    :return: one if the update operation was successful, none if not
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
    Delete the action record from the actions db table

    :param user_id: Telegram user id derived from call or message
    :param action_id: Action id derived from the cache
    :param db_session: AsyncSession derived from the middleware
    :return: one if the delete operation was successful, none if not
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
