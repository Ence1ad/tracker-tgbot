import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
# import sqlalchemy as sa

from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError, DBAPIError

from db.actions.actions_db_commands import create_actions
from db.categories.categories_commands import create_category
from db.categories.categories_model import CategoriesModel
from db.tracker.tracker_db_command import create_tracker
from db.users.user import UserModel
from db.users.users_commands import create_user


@pytest.mark.parametrize(
    "user_id, category_name, expectation",
    [
        (1111111111, 'new_cat', does_not_raise()),
        (1111111111, 'new_category', does_not_raise()),
        (1111111111, 'new_category', pytest.raises(IntegrityError)),
        (1111111111, None, pytest.raises(IntegrityError)),
        (1111111111, '', pytest.raises(IntegrityError)),
        (None, 'best_cat', pytest.raises(IntegrityError)),
        (1111111112, 'new_cat', does_not_raise()),
        (1111111112, 'best_cat', does_not_raise()),
        (1111111112, 12345, pytest.raises(DBAPIError)),
        ('abc', 'some_cat', pytest.raises(DBAPIError)),


    ]
)
@pytest.mark.asyncio
async def test_create_category(
        session: AsyncSession,
        user_id: int,
        category_name: str,
        expectation: does_not_raise,
        add_user
):
    with expectation:
        category_obj: CategoriesModel = await create_category(user_id, category_name, db_session=session)
        assert all(
            [
                # category_obj.category_id == 1,
                category_obj.category_name == category_name,
                category_obj.user_id == user_id
            ]
        )

@pytest.mark.parametrize(
    "user_id, first_name, last_name, username, expectation",
    [
        (1000000001, 'Ivan', 'Ivanov', 'Rus', does_not_raise()),
        (1000000001, '', '', '', pytest.raises(IntegrityError)),
        (1000000002, 'Ivan', 'Ivanov', 'Rus', does_not_raise()),
        (1000000003, 'Ivan', 'Ivanov', None, does_not_raise()),
        (1000000004, 'Ivan', None, None, does_not_raise()),
        (1000000005, None, None, None, does_not_raise()),
        (1000000006, '', '', '', does_not_raise()),
        (None, '', '', '', pytest.raises(IntegrityError)),
        ('abc', '', '', '', pytest.raises(DBAPIError)),
        (1000000007, 123, '', '', pytest.raises(DBAPIError)),
        (1000000008, '', 123, '', pytest.raises(DBAPIError)),
        (1000000009, '', '', 123, pytest.raises(DBAPIError)),
        (1000000010, 123, 123, 123, pytest.raises(DBAPIError)),
    ]
)
@pytest.mark.asyncio
async def test_create_user(
        session: AsyncSession,
        user_id: int,
        first_name: str,
        last_name: str,
        username: str,
        expectation: does_not_raise
):
    with expectation:
        user_model: UserModel = await create_user(user_id, first_name, last_name, username, db_session=session)
        assert user_model.user_id == user_id
        # print((await session.execute(sa.select(UserModel.user_id))).scalar())
        # print(type((await session.execute(sa.select(UserModel.user_id))).scalar()))

        # assert len((await session.execute(sa.select(UserModel))).scalars().all()) == 1
        # assert type((await session.execute(sa.select(UserModel.user_id))).scalar()) == int


@pytest.mark.parametrize(
    "user_id, action_name, category_id, expectation",
    [
        (1111111111, 'new_action', 1, does_not_raise()),
        (1111111111, 'new_act', 1, does_not_raise()),
        (1111111111, 'new_act', -1, pytest.raises(IntegrityError)),
        (1111111111, 'new_act', None, pytest.raises(IntegrityError)),
        (1111111111, '', 1, pytest.raises(IntegrityError)),
        (1111111111, None, 1, pytest.raises(IntegrityError)),
        (None, 'best_act', 1, pytest.raises(IntegrityError)),
        ('string', 'some_act', 1, pytest.raises(DBAPIError)),
    ]
)

@pytest.mark.asyncio
async def test_create_action(
        session: AsyncSession,
        user_id: int,
        category_id: int,
        action_name: str,
        expectation: does_not_raise,
        add_category
):
    with expectation:
        action_obj = await create_actions(user_id, category_id=category_id, action_name=action_name, db_session=session)
        assert action_obj.action_name == action_name


# @pytest.mark.parametrize(
#     "user_id, category_name, action_id, expectation",
#     [
#         (1111111111, 'best_category_ever', 1, does_not_raise()),
#     ]
# )
# @pytest.mark.asyncio
# async def test_create_tracker(
#         session: AsyncSession,
#         user_id: int,
#         action_id: int,
#         category_name: str,
#         expectation: does_not_raise,
#         add_action,
#         add_category,
# ):
#     with expectation:
#         await create_tracker(
#             user_id=user_id,
#             action_id=action_id,
#             category_name=category_name,
#             track_start=datetime.datetime.now(),
#             db_session=session
#         )
