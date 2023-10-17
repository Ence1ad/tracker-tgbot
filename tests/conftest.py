from collections.abc import Callable
from typing import Any

import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db import UserModel, CategoryModel
from db.operations.actions_operations import create_actions
from db.operations.tracker_operations import create_tracker
from tests.utils import MAIN_USER_ID, ACTION_NAME, CATEGORY_NAME, \
    OTHER_USER_ID, USER_ID_WITH_TRACKER_LIMIT


@pytest_asyncio.fixture(scope='class')
async def db_user_factory(db_session_fixture: AsyncSession
                          ) -> Callable[[Any, Any], Any]:
    """Creates user records in the database.

    :param db_session_fixture: AsyncSession: An asynchronous database session.
    :return: Callable: An asynchronous function that creates a user record and returns
    the user_id.
    """
    async def _create_user(user_id: int, first_name: str = 'some_name',
                           last_name: str = '', username: str = '') -> int | None:
        """Creates a user record in the database.

        :param user_id: int: The user's unique identifier.
        :param first_name: str: The user's first name (default: 'some_name').
        :param last_name: str: The user's last name (default: '').
        :param username: str: The user's username (default: '').
        :return: int or None: The user_id if the user is created successfully,
        or None in case of an integrity error.
        """
        user = UserModel(user_id=user_id, first_name=first_name, last_name=last_name,
                         username=username)
        db_session_fixture.add(user)
        try:
            await db_session_fixture.commit()
            return user_id
        except IntegrityError:
            await db_session_fixture.rollback()
            return None

    return _create_user


@pytest_asyncio.fixture(scope='class')
async def db_category_factory(
        db_user_factory: Callable[[Any], Any], db_session_fixture: AsyncSession
) -> Callable[[Any, Any], Any]:
    """
    Creates category records in the database associated with a user.

    :param db_user_factory: A fixture to create user records.
    :param db_session_fixture: AsyncSession: An asynchronous database session.
    :return: Callable: An asynchronous function that creates a category record and
    returns the category.
    """
    async def _db_category_factory(user_id: int, category_name: str = CATEGORY_NAME
                                   ) -> CategoryModel | None:
        """Creates a category record associated with a user in the database.

        :param user_id: int: The user's unique identifier.
        :param category_name: str: The name of the category (default: CATEGORY_NAME).
        :return: CategoryModel or None: The created category if successful,
        or None in case of an integrity error.
        """
        await db_user_factory(user_id)
        try:
            category = CategoryModel(user_id=user_id, category_name=category_name)
            db_session_fixture.add(category)
            await db_session_fixture.commit()
            return category
        except IntegrityError:
            await db_session_fixture.rollback()
            return None

    return _db_category_factory


@pytest_asyncio.fixture(scope="class")
async def add_data_to_db(db_user_factory, db_session_fixture, db_category_factory
                         ):
    """Adds initial data to the db, including users, categories, actions, and a tracker.

    :param db_user_factory: A fixture to create user records.
    :param db_category_factory: A fixture to create category records.
    :param db_session_fixture: An asynchronous database session fixture.
    :return: None
    """
    users = [MAIN_USER_ID, OTHER_USER_ID, USER_ID_WITH_TRACKER_LIMIT]

    tracker_obj = None
    for user_id in users:
        user_id = await db_user_factory(user_id=user_id)
        category_obj = await db_category_factory(user_id)
        category_id = category_obj.category_id
        action_obj = await create_actions(
            user_id=user_id, action_name=ACTION_NAME,
            category_id=category_id, db_session=db_session_fixture
        )
        tracker_obj = await create_tracker(
            user_id=user_id, category_id=category_id,
            action_id=action_obj.action_id, db_session=db_session_fixture
        )
    yield tracker_obj
