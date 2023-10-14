import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError, DBAPIError, ProgrammingError

from db import ActionsModel
from db.operations.actions_operations import create_actions, select_category_actions, delete_action, update_action_name
from tests.utils import MAIN_USER_ID


@pytest.mark.usefixtures('add_data_to_db')
@pytest.mark.asyncio
class TestActions:
    @pytest.mark.parametrize(
        "user_id, action_name, category_id, expectation",
        [
            (MAIN_USER_ID, 'new_action', 1, does_not_raise()),
            (MAIN_USER_ID, 'new_act', 1, does_not_raise()),
            (MAIN_USER_ID, 'new_act', -1, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, 'new_act', None, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, '', 1, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, None, 1, pytest.raises(IntegrityError)),
            (None, 'best_act', 1, pytest.raises(IntegrityError)),
            ('string', 'some_act', 1, pytest.raises(DBAPIError)),
        ]
    )
    async def test_create_action(
            self,
            db_session: async_sessionmaker[AsyncSession],
            user_id: int,
            action_name: str,
            category_id: int,
            expectation: does_not_raise,
    ):
        with expectation:
            action_obj = await create_actions(user_id, category_id=category_id, action_name=action_name,
                                              db_session=db_session)
            assert isinstance(action_obj, ActionsModel)
            assert action_obj.action_name == action_name

    @pytest.mark.parametrize(
        "user_id, category_id, expectation",
        [
            (MAIN_USER_ID, 1, does_not_raise()),
            (MAIN_USER_ID, -1, pytest.raises(AssertionError)),
            (MAIN_USER_ID, '1', pytest.raises(ProgrammingError)),
            ('MAIN_USER_ID', 1, pytest.raises(ProgrammingError)),
            (MAIN_USER_ID, None, pytest.raises(AssertionError)),
            (None, 1, pytest.raises(AssertionError)),
            (10000000001, 1, pytest.raises(AssertionError)),

        ]
    )
    async def test_select_category_actions(
            self,
            db_session: async_sessionmaker[AsyncSession],
            user_id: int,
            category_id: int,
            expectation: does_not_raise,
    ):
        with expectation:
            actions_fetchall = await select_category_actions(user_id, category_id, db_session=db_session)
            assert actions_fetchall != []

    @pytest.mark.parametrize(
        "user_id, action_id, new_action_name, expectation",
        [
            (MAIN_USER_ID, 1, 'new_name', does_not_raise()),
            (MAIN_USER_ID, 1, 'user_cool_action_name', pytest.raises(DBAPIError)),  # name > 20 chars
            (MAIN_USER_ID, '1', 'new_name', pytest.raises(DBAPIError)),
            ('MAIN_USER_ID', 1, 'new_name', pytest.raises(DBAPIError)),
            (MAIN_USER_ID, 1, 123, pytest.raises(DBAPIError)),
            (MAIN_USER_ID, 1, '', pytest.raises(IntegrityError)),
            (MAIN_USER_ID, 1, None, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, None, 'new_name', pytest.raises(AssertionError)),
            (MAIN_USER_ID, -1, 'new_name', pytest.raises(AssertionError)),
            (-1, 1, 'new_name', pytest.raises(AssertionError)),
            (None, 1, 'new_name', pytest.raises(AssertionError)),
        ]
    )
    async def test_update_action(
            self,
            db_session: async_sessionmaker[AsyncSession],
            user_id: int,
            action_id: int,
            new_action_name: str,
            expectation: does_not_raise
    ):
        with expectation:
            res_id_scalar_one_or_none: int = await update_action_name(user_id, action_id, new_action_name, db_session)
            assert isinstance(res_id_scalar_one_or_none, int)
            assert res_id_scalar_one_or_none == 1

    @pytest.mark.parametrize(
        "user_id, action_id, expectation",
        [
            (MAIN_USER_ID, 1, does_not_raise()),
            (MAIN_USER_ID, '1', pytest.raises(DBAPIError)),
            ('MAIN_USER_ID', 1, pytest.raises(DBAPIError)),
            (MAIN_USER_ID, None, pytest.raises(AssertionError)),
            (MAIN_USER_ID, -1, pytest.raises(AssertionError)),
            (-1, 1, pytest.raises(AssertionError)),
            (None, 1, pytest.raises(AssertionError)),
        ]
    )
    async def test_delete_action(
            self,
            db_session: async_sessionmaker[AsyncSession],
            user_id: int,
            action_id: int,
            expectation: does_not_raise
    ):
        with expectation:
            res_id_scalar_one_or_none = await delete_action(user_id, action_id, db_session)
            assert res_id_scalar_one_or_none == 1
