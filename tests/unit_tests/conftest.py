import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


from cache.redis_tracker_commands import redis_hmset_create_tracker, redis_delete_tracker

from db import UserModel
from db.actions.actions_db_commands import create_actions
from db.categories.categories_commands import create_category
from db.tracker.tracker_db_command import create_tracker
from db.users.users_commands import create_user
from tests.unit_tests.utils import MAIN_USER_ID, ACTION_NAME, CATEGORY_NAME, \
    SECOND_USER_ID, USER_ID_WITH_TRACKER_LIMIT


@pytest_asyncio.fixture(scope='class')
async def db_session(async_session):
    async with async_session() as db_session:
        yield db_session


@pytest_asyncio.fixture(scope='class')
async def db_user_factory(db_session: async_sessionmaker[AsyncSession]):
    async def _db_user_factory(user_id):
        async with db_session as db_sess:
            stmt: Result = await db_sess.execute(sa.select(UserModel).where(UserModel.user_id == user_id))
            user = stmt.scalar_one_or_none()
        if user is None:
            user_obj = await create_user(user_id=user_id, first_name='', last_name='', username='',
                                         db_session=db_session)
            return user_obj.user_id
    return _db_user_factory


@pytest_asyncio.fixture(scope='class')
async def db_category_factory(db_user_factory, db_session: async_sessionmaker[AsyncSession]):
    async def _db_category_factory(user_id, category_name: str = CATEGORY_NAME):
        await db_user_factory(user_id)
        try:
            category_obj = await create_category(user_id=user_id, category_name=category_name, db_session=db_session)
            return category_obj
        except IntegrityError as ex:
            return
    return _db_category_factory


@pytest_asyncio.fixture(scope="class")
async def add_data_to_db(db_user_factory, db_category_factory,  db_session,):
    users = [MAIN_USER_ID, SECOND_USER_ID, USER_ID_WITH_TRACKER_LIMIT]

    tracker_obj = None
    for user_id in users:

        user_id = await db_user_factory(user_id=user_id)
        category_obj = await db_category_factory(user_id)
        category_id = category_obj.category_id
        action_obj = await create_actions(user_id=user_id, action_name=ACTION_NAME,
                                          category_id=category_id, db_session=db_session)
        tracker_obj = await create_tracker(user_id=user_id, category_id=category_id,
                                           action_id=action_obj.action_id, db_session=db_session)
    yield tracker_obj
    # for user_id in users:
    #     await delete_tracker(user_id=user_id, tracker_id=tracker_obj.tracker_id, db_session=db_session)
    #     await delete_action(user_id=user_id, action_id=action_obj.action_id, db_session=db_session)
    #     await delete_category(user_id=user_id, category_id=category_obj.category_id, db_session=db_session)
    #     await db_session.execute(sa.delete(UserModel).where(UserModel.user_id == user_id))

@pytest_asyncio.fixture(scope='class')
async def create_tracker_fixt(add_data_to_db, redis_cli):
    tracker_obj = add_data_to_db
    user_id = USER_ID_WITH_TRACKER_LIMIT
    tracker = await redis_hmset_create_tracker(
        user_id=user_id, tracker_id=tracker_obj.tracker_id, action_id=tracker_obj.action_id, action_name='',
        category_id=tracker_obj.category_id, category_name='', redis_client=redis_cli)
    yield tracker
    await redis_delete_tracker(user_id=user_id, redis_client=redis_cli)








