from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError, DBAPIError, ProgrammingError

from db import ActionModel
from db.operations.actions_operations import create_actions, select_category_actions, \
    delete_action, update_action_name
from tests.utils import MAIN_USER_ID, OTHER_USER_ID, NONE_USER_ID, \
    ABSENT_IN_DB_USER_ID, INVALID_USER_ID


@pytest.mark.usefixtures('add_data_to_db')
@pytest.mark.asyncio
class TestActions:
    @pytest.mark.parametrize(
        "user_id, action_name, category_id, expectation",
        [
            (MAIN_USER_ID, 'new_action', 1, does_not_raise()),
            (OTHER_USER_ID, 'new_act', 2, does_not_raise()),
            (MAIN_USER_ID, 'new_act', -1, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, 'new_act', None, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, '', 1, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, None, 1, pytest.raises(IntegrityError)),
            (NONE_USER_ID, 'best_act', 1, pytest.raises(IntegrityError)),
            (INVALID_USER_ID, 'some_act', 1, pytest.raises(DBAPIError)),
        ]
    )
    async def test_create_action(
            self, db_session_fixture: AsyncSession, user_id: int, action_name: str,
            category_id: int, expectation: Any,
    ) -> None:
        with expectation:
            action_obj = await create_actions(
                user_id, category_id=category_id, action_name=action_name,
                db_session=db_session_fixture
            )
            assert isinstance(action_obj, ActionModel)
            assert action_obj.action_name == action_name

    @pytest.mark.parametrize(
        "user_id, category_id, expectation",
        [
            (MAIN_USER_ID, 1, does_not_raise()),
            (OTHER_USER_ID, 2, does_not_raise()),
            (MAIN_USER_ID, -1, pytest.raises(AssertionError)),
            (MAIN_USER_ID, '1', pytest.raises(ProgrammingError)),
            (INVALID_USER_ID, 1, pytest.raises(ProgrammingError)),
            (MAIN_USER_ID, None, pytest.raises(AssertionError)),
            (NONE_USER_ID, 1, pytest.raises(AssertionError)),
            (ABSENT_IN_DB_USER_ID, 1, pytest.raises(AssertionError)),

        ]
    )
    async def test_select_category_actions(
            self, db_session_fixture: AsyncSession, user_id: int, category_id: int,
            expectation: Any,
    ) -> None:
        with expectation:
            actions_fetchall = await select_category_actions(
                user_id, category_id, db_session=db_session_fixture
            )
            assert isinstance(actions_fetchall, list)
            assert actions_fetchall

    @pytest.mark.parametrize(
        "user_id, action_id, new_action_name, expectation",
        [
            (MAIN_USER_ID, 1, 'new_name', does_not_raise()),
            (OTHER_USER_ID, 2, 'new_name', does_not_raise()),
            (ABSENT_IN_DB_USER_ID, 2, 'new_name', pytest.raises(AssertionError)),
            (MAIN_USER_ID, 1, 'user_cool_action_name', pytest.raises(  # name > 20 chars
                DBAPIError)),
            (MAIN_USER_ID, '1', 'new_name', pytest.raises(DBAPIError)),
            (INVALID_USER_ID, 1, 'new_name', pytest.raises(DBAPIError)),
            (MAIN_USER_ID, 1, 123, pytest.raises(DBAPIError)),
            (MAIN_USER_ID, 1, '', pytest.raises(IntegrityError)),
            (MAIN_USER_ID, 1, None, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, None, 'new_name', pytest.raises(AssertionError)),
            (MAIN_USER_ID, -1, 'new_name', pytest.raises(AssertionError)),
            (NONE_USER_ID, 1, 'new_name', pytest.raises(AssertionError)),
        ]
    )
    async def test_update_action(
            self, db_session_fixture: AsyncSession, user_id: int, action_id: int,
            new_action_name: str, expectation: Any
    ) -> None:
        with expectation:
            res_id_scalar_one_or_none: int | None = await update_action_name(
                user_id, action_id, new_action_name, db_session_fixture
            )
            assert isinstance(res_id_scalar_one_or_none, int)
            assert res_id_scalar_one_or_none == action_id

    @pytest.mark.parametrize(
        "user_id, action_id, expectation",
        [
            (MAIN_USER_ID, 1, does_not_raise()),
            (OTHER_USER_ID, 2, does_not_raise()),
            (MAIN_USER_ID, '1', pytest.raises(DBAPIError)),
            (INVALID_USER_ID, 1, pytest.raises(DBAPIError)),
            (MAIN_USER_ID, None, pytest.raises(AssertionError)),
            (MAIN_USER_ID, -1, pytest.raises(AssertionError)),
            (ABSENT_IN_DB_USER_ID, 1, pytest.raises(AssertionError)),
            (NONE_USER_ID, 1, pytest.raises(AssertionError)),
        ]
    )
    async def test_delete_action(
            self, db_session_fixture: AsyncSession, user_id: int, action_id: int,
            expectation: Any
    ) -> None:
        with expectation:
            res_id_scalar_one_or_none = await delete_action(
                user_id, action_id, db_session_fixture
            )
            assert isinstance(res_id_scalar_one_or_none, int)
            assert res_id_scalar_one_or_none == action_id
