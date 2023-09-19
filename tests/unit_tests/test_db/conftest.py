import pytest
import pytest_asyncio

from db.actions.actions_db_commands import create_actions
from db.categories.categories_commands import create_category
from db.users.users_commands import create_user


@pytest.mark.usefixtures('set_user_id')
@pytest_asyncio.fixture(scope="class")
async def add_user(session, set_user_id):
    user_id: int = set_user_id
    for i in range(3):
        await create_user(user_id=user_id + i, first_name='', last_name='', username='',
                          db_session=session)
    # yield user_obj
    # await session.execute(sa.delete(UserModel).where(UserModel.user_id == user_id))


@pytest.mark.usefixtures('set_user_id')
@pytest_asyncio.fixture(scope="class")
async def add_category(session, add_user, set_user_id):
    category_name = 'best_category_ever'
    await create_category(user_id=set_user_id, category_name=category_name, db_session=session)
    # yield category_obj
    # await delete_category(user_id=USER_ID, category_id=category_obj.category_id, db_session=session)


@pytest.mark.usefixtures('set_user_id')
@pytest_asyncio.fixture(scope="class")
async def add_action(session, add_category, set_user_id):
    action_name = 'my_action'
    category_id = 1
    await create_actions(user_id=set_user_id, action_name=action_name, category_id=category_id,
                         db_session=session)
    # yield action_obj
    # await delete_action(user_id=USER_ID, action_id=action_obj.action_id, db_session=session)
