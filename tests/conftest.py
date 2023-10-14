import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db import UserModel, CategoriesModel
from db.operations.actions_operations import create_actions
from db.operations.tracker_operations import create_tracker
from tests.utils import MAIN_USER_ID, ACTION_NAME, CATEGORY_NAME, \
    OTHER_USER_ID, USER_ID_WITH_TRACKER_LIMIT


@pytest_asyncio.fixture(scope='class')
async def db_user_factory(db_session: AsyncSession):
    async def _create_user(user_id, first_name='some_name', last_name='', username=''):
        user = UserModel(user_id=user_id, first_name=first_name, last_name=last_name, username=username)
        db_session.add(user)
        try:
            await db_session.commit()
            return user_id
        except IntegrityError:
            await db_session.rollback()
            return None

    return _create_user


@pytest_asyncio.fixture(scope='class')
async def db_category_factory(db_user_factory, db_session: AsyncSession):
    async def _db_category_factory(user_id, category_name=CATEGORY_NAME):
        await db_user_factory(user_id)
        try:
            category = CategoriesModel(user_id=user_id, category_name=category_name)
            db_session.add(category)
            await db_session.commit()
            return category
        except IntegrityError:
            await db_session.rollback()
            return None

    return _db_category_factory


@pytest_asyncio.fixture(scope="class")
async def add_data_to_db(db_user_factory, db_category_factory,  db_session,):
    users = [MAIN_USER_ID, OTHER_USER_ID, USER_ID_WITH_TRACKER_LIMIT]

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
