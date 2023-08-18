from sqlalchemy import select, delete, update

from ..categories.categories_model import CategoriesModel
from ..db_session import create_async_session
from .actions_models import ActionsModel


async def create_actions(user_id: int, action_name: str, category_id: str) -> None:
    # TODO необходима проверка существует ли категория перед созданием действия
    async with await create_async_session() as session:
        async with session.begin():
            create_action: ActionsModel = ActionsModel(action_name=action_name,
                                                       category_id=category_id,
                                                       user_id=user_id
                                                       )
            session.add(create_action)


async def get_user_actions(user_id: int, category_id: int):
    async with await create_async_session() as session:
        async with session.begin():
            stmt = \
                select(ActionsModel.action_id, ActionsModel.action_name, CategoriesModel.category_name).join(
                    CategoriesModel) \
                .where(ActionsModel.user_id == user_id, ActionsModel.category_id == category_id)
            return await session.execute(stmt)


async def delete_action(user_id: int, action_id: int) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = delete(ActionsModel).where(ActionsModel.user_id == user_id,
                                              ActionsModel.action_id == action_id)
            await session.execute(stmt)


async def update_action(user_id: int, action_id: int, new_action_name: int) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = update(ActionsModel).where(ActionsModel.user_id == user_id, ActionsModel.action_id == action_id) \
                .values(action_name=new_action_name)
            await session.execute(stmt)


async def check_action(user_id: int, action_name: str, category_id: int) -> str | None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = select(ActionsModel.action_name).join(CategoriesModel).where(
                ActionsModel.user_id == user_id, ActionsModel.category_id == category_id)
            res = await session.execute(stmt)
            user_actions = res.scalars().all()
            action_limit = 10
            if user_actions and (len(user_actions) < action_limit):
                for action in user_actions:
                    if str(action_name) == action:
                        return None
                else:
                    return action_name[:30]
            else:
                return 'action_limit'
