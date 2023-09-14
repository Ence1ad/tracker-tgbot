import asyncio
import sys

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from db.actions.actions_db_commands import create_actions
from db.base_model import SqlAlchemyBase
from db.categories.categories_commands import create_category
from db.users.users_commands import create_user

from config import settings

USER_ID = 1111111111


@pytest.fixture(scope="package")
def event_loop():
    """
    Creates an instance of the default event loop for the test session.
    """
    if sys.platform.startswith("win") and sys.version_info[:2] >= (3, 8):
        # Avoid "RuntimeError: Event loop is closed" on Windows when tearing down tests
        # https://github.com/encode/httpx/issues/914
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="package")
def async_engine():
    if settings.TESTING:
        engine = create_async_engine(
            settings.db_url
        )
        yield engine
        engine.sync_engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def create_drop_models(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(SqlAlchemyBase.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(SqlAlchemyBase.metadata.drop_all)


@pytest_asyncio.fixture(scope="class")
async def session(async_engine, create_drop_models):
    async with AsyncSession(async_engine) as db_session:
        yield db_session


@pytest_asyncio.fixture(scope="class")
async def add_user(session):
    user_id: int = USER_ID
    for i in range(3):
        user_obj = await create_user(user_id=user_id + i, first_name='', last_name='', username='',
                                     db_session=session)
    # yield user_obj
    # await session.execute(sa.delete(UserModel).where(UserModel.user_id == user_id))


@pytest_asyncio.fixture(scope="class")
async def add_category(session, add_user):
    category_name = 'best_category_ever'
    await create_category(user_id=USER_ID, category_name=category_name, db_session=session)
    # yield category_obj
    # await delete_category(user_id=USER_ID, category_id=category_obj.category_id, db_session=session)


@pytest_asyncio.fixture(scope="class")
async def add_action(session, add_category):
    action_name = 'my_action'
    category_id = 1
    await create_actions(user_id=USER_ID, action_name=action_name, category_id=category_id,
                                      db_session=session)
    # yield action_obj
    # await delete_action(user_id=USER_ID, action_id=action_obj.action_id, db_session=session)
