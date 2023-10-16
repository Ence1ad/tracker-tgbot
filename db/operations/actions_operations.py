from sqlalchemy import select, delete, update, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.action_model import ActionModel


async def create_actions(user_id: int, action_name: str, category_id: int,
                         db_session: AsyncSession) -> ActionModel:
    """Create a new action record in the database.

    :param user_id: The identifier of the associated user.
    :param action_name: The name of the action.
    :param category_id: The identifier of the associated category.
    :param db_session: The asynchronous database session.

    :return: The newly created ActionModel object representing the action.
    """
    async with db_session as session:
        async with session.begin():
            action_obj: ActionModel = \
                ActionModel(action_name=action_name,
                            category_id=category_id,
                            user_id=user_id)
            session.add(action_obj)
            await session.flush()

        await session.refresh(action_obj)
        return action_obj


async def select_category_actions(user_id: int, category_id: int,
                                  db_session: AsyncSession) -> Sequence:
    """Select actions of a specific category from the database.

    :param user_id: The identifier of the associated user.
    :param category_id: The identifier of the category to select actions from.
    :param db_session: The asynchronous database session.

    :return: A list of action records (ActionModel) within the specified category.
    """
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(ActionModel.action_id,
                       ActionModel.action_name)\
                .where(ActionModel.user_id == user_id,
                       ActionModel.category_id == category_id)\
                .order_by(ActionModel.action_name)

            res = await session.execute(stmt)
            return res.fetchall()


async def update_action_name(user_id: int, action_id: int, new_action_name: str,
                             db_session: AsyncSession) -> int | None:
    """Update the name of an existing action in the database.

    :param user_id: The identifier of the associated user.
    :param action_id: The identifier of the action to be updated.
    :param new_action_name: The new name for the action.
    :param db_session: The asynchronous database session.

    :return: The identifier of the updated action if successful, None otherwise.
    """
    async with db_session as session:
        async with session.begin():
            udp_stmt = \
                update(ActionModel)\
                .where(ActionModel.user_id == user_id,
                       ActionModel.action_id == action_id) \
                .values(action_name=new_action_name)\
                .returning(ActionModel.action_id)

            returning = await session.execute(udp_stmt)
            return returning.scalar_one_or_none()


async def delete_action(user_id: int, action_id: int, db_session: AsyncSession
                        ) -> int | None:
    """Delete an action record from the database.

    :param user_id: The identifier of the associated user.
    :param action_id: The identifier of the action to be deleted.
    :param db_session: The asynchronous database session.

    :return: The identifier of the deleted action if successful, None otherwise.
    """
    async with db_session as session:
        async with session.begin():
            del_stmt = \
                delete(ActionModel)\
                .where(ActionModel.user_id == user_id,
                       ActionModel.action_id == action_id)\
                .returning(ActionModel.action_id)

            returning = await session.execute(del_stmt)
            return returning.scalar_one_or_none()
