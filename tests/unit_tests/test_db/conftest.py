
import pytest_asyncio
import sqlalchemy as sa

from db import UserModel
from db.actions.actions_db_commands import create_actions, delete_action
from db.categories.categories_commands import create_category, delete_category
from db.users.users_commands import create_user

DB_USER_ID: int = 1111111111


@pytest_asyncio.fixture(scope="class")
async def db_user(db_session):
    user_id: int = DB_USER_ID
    user_obj = await create_user(user_id=user_id, first_name='', last_name='', username='',
                                 db_session=db_session)
    try:
        yield user_obj.user_id
    finally:
        await db_session.execute(sa.delete(UserModel).where(UserModel.user_id == user_id))


@pytest_asyncio.fixture(scope="class")
async def add_category(db_session):
    category_name = 'best_category_ever'
    user_obj = await create_user(user_id=DB_USER_ID, first_name='', last_name='', username='',
                                 db_session=db_session)
    category_obj = await create_category(user_id=user_obj.user_id, category_name=category_name, db_session=db_session)
    try:
        yield category_obj.category_id
    finally:
        await delete_category(user_id=user_obj.user_id, category_id=category_obj.category_id, db_session=db_session)
        await db_session.execute(sa.delete(UserModel).where(UserModel.user_id == DB_USER_ID))


@pytest_asyncio.fixture(scope="class")
async def add_action(db_session):
    user_obj = await create_user(user_id=DB_USER_ID, first_name='', last_name='', username='',
                                 db_session=db_session)
    category_name = 'best_category_ever'
    category_obj = await create_category(user_id=user_obj.user_id, category_name=category_name, db_session=db_session)
    action_name = 'my_action'
    action_obj = await create_actions(user_id=user_obj.user_id, action_name=action_name,
                                      category_id=category_obj.category_id, db_session=db_session)
    try:
        yield action_obj
    finally:
        await delete_action(user_id=DB_USER_ID, action_id=action_obj.action_id, db_session=db_session)
        await delete_category(user_id=user_obj.user_id, category_id=category_obj.category_id, db_session=db_session)
        await db_session.execute(sa.delete(UserModel).where(UserModel.user_id == DB_USER_ID))
