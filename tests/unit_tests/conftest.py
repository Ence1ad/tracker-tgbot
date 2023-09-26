import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


from cache.redis_tracker_commands import redis_hmset_create_tracker, redis_delete_tracker
from config import settings
from db import UserModel
from db.actions.actions_db_commands import create_actions, delete_action
from db.categories.categories_commands import create_category, delete_category
from db.tracker.tracker_db_command import create_tracker
from db.users.users_commands import create_user
from tests.unit_tests.utils import MAIN_USER_ID, ACTION_NAME, CATEGORY_ID, CATEGORY_NAME, \
    SECOND_USER_ID


# @pytest_asyncio.fixture
# async def create_tg_user():  # fixture factory
#     async def _create_tg_user(user_id, first_name='test_name', is_bot=False, lang_code=LANG_CODE):
#         return User(id=user_id, first_name=first_name, is_bot=is_bot, language_code=lang_code)
#     return _create_tg_user

@pytest_asyncio.fixture(scope='class')
async def db_session(async_session):
    async with async_session() as db_session:
        yield db_session


@pytest_asyncio.fixture
async def create_tracker_fixt(add_data_to_db, redis_cli):
    tracker = None
    tracker_obj = add_data_to_db
    users = [MAIN_USER_ID, SECOND_USER_ID]
    for user in users:
        tracker = await redis_hmset_create_tracker(
            user_id=user, tracker_id=tracker_obj.tracker_id, action_id=tracker_obj.action_id, action_name='',
            category_id=tracker_obj.category_id, category_name='', redis_client=redis_cli)
    yield tracker
    await redis_delete_tracker(user_id=MAIN_USER_ID, redis_client=redis_cli)


@pytest_asyncio.fixture
async def create_tracker_fixt_fact(redis_cli):
    async def _create_tracker_fixt_fact(user_id: int, category_id: int, category_name: str, action_id: int, action_name,
                                        tracker_id: str):
        tracker = await redis_hmset_create_tracker(
            user_id=user_id, tracker_id=tracker_id, action_id=action_id, action_name=action_name,
            category_id=category_id, category_name=category_name, redis_client=redis_cli
        )
        return tracker
    return _create_tracker_fixt_fact


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
async def add_data_to_db(db_user_factory, db_category_factory,  db_session):
    users = [MAIN_USER_ID, SECOND_USER_ID]
    tracker_obj = None
    for user in users:
        user_id = await db_user_factory(user_id=user)
        category_obj = await db_category_factory(user_id)
        category_id = category_obj.category_id
        action_obj = await create_actions(user_id=user_id, action_name=ACTION_NAME,
                                          category_id=category_id, db_session=db_session)
        tracker_obj = await create_tracker(user_id=user_id, category_id=category_obj.category_id,
                                           action_id=action_obj.action_id, db_session=db_session)

    yield tracker_obj
    # finally:
    #     await delete_action(user_id=user_id, action_id=action_obj.action_id, db_session=db_session)
    #     await delete_category(user_id=user_id, category_id=category_obj.category_id, db_session=db_session)
    #     await db_session.execute(sa.delete(UserModel).where(UserModel.user_id == user_id))


@pytest_asyncio.fixture(scope="class")
async def create_categories_more_than_limit(db_user_factory, db_session: async_sessionmaker[AsyncSession]):
    user_id = await db_user_factory(MAIN_USER_ID)
    for name in range(settings.USER_CATEGORIES_LIMIT):
        await create_category(user_id=user_id, category_name=str(name), db_session=db_session)
    try:
        yield
    finally:
        for cat_id in range(settings.USER_CATEGORIES_LIMIT):
            await delete_category(user_id=user_id, category_id=cat_id+1, db_session=db_session)


@pytest_asyncio.fixture(scope="class")
async def create_actions_more_than_limit(db_session: async_sessionmaker[AsyncSession]):
    user_id = MAIN_USER_ID
    for name in range(settings.USER_ACTIONS_LIMIT):
        await create_actions(user_id=user_id, category_id=CATEGORY_ID, action_name=str(name), db_session=db_session)
    try:
        yield
    finally:
        for act_id in range(settings.USER_ACTIONS_LIMIT):
            await delete_action(user_id=user_id, action_id=act_id+1, db_session=db_session)


