from datetime import timedelta
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError, DBAPIError, ProgrammingError

from db.operations.report_operations import select_weekly_trackers
from db.operations.tracker_operations import create_tracker, select_tracker_duration, \
    delete_tracker, select_stopped_trackers
from tests.utils import MAIN_USER_ID, OTHER_USER_ID, NONE_USER_ID, \
    ABSENT_IN_DB_USER_ID, INVALID_USER_ID


@pytest.mark.usefixtures('add_data_to_db')
@pytest.mark.asyncio
class TestTrackers:
    @pytest.mark.parametrize(
        "user_id, category_id, action_id, expectation",
        [
            (MAIN_USER_ID, 1, 1, does_not_raise()),
            (OTHER_USER_ID, 2, 1, does_not_raise()),
            (MAIN_USER_ID, 1, -1, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, -1, 1, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, 1, None, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, None, 1, pytest.raises(IntegrityError)),
            (NONE_USER_ID, 1, 1, pytest.raises(IntegrityError)),
            (MAIN_USER_ID, '1', 1, pytest.raises(DBAPIError)),
            (MAIN_USER_ID, 1, '1', pytest.raises(DBAPIError)),
            ('MAIN_USER_ID', 1, 1, pytest.raises(DBAPIError)),
        ]
    )
    async def test_create_tracker(
            self, db_session_fixture: AsyncSession, user_id: int, action_id: int,
            category_id: int, expectation: Any,
    ) -> None:
        with expectation:
            tracker_obj = await create_tracker(
                user_id=user_id,
                action_id=action_id,
                category_id=category_id,
                db_session=db_session_fixture
            )
            assert tracker_obj.user_id == user_id
            assert tracker_obj.duration is None

    @pytest.mark.parametrize(
        ['user_id', 'tracker_id', 'expectation'],
        [
            (MAIN_USER_ID, 1, does_not_raise()),
            (OTHER_USER_ID, 2, does_not_raise()),
            (MAIN_USER_ID, '1', pytest.raises(DBAPIError)),
            ('MAIN_USER_ID', 1, pytest.raises(DBAPIError)),
            (MAIN_USER_ID, None, pytest.raises(AssertionError)),
            (MAIN_USER_ID, -1, pytest.raises(AssertionError)),
            (ABSENT_IN_DB_USER_ID, 1, pytest.raises(AssertionError)),
            (NONE_USER_ID, 1, pytest.raises(AssertionError)),
        ]
             )
    async def test_stop_tracker(
            self, db_session_fixture: AsyncSession, user_id: int, tracker_id: int,
            expectation: Any,
    ) -> None:
        with expectation:
            duration_returning = await select_tracker_duration(
                user_id, tracker_id, db_session=db_session_fixture
            )
            assert isinstance(duration_returning, timedelta)
            assert duration_returning

    @pytest.mark.parametrize(
        ['user_id', 'expectation'],
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            (ABSENT_IN_DB_USER_ID, pytest.raises(AssertionError)),
            (INVALID_USER_ID, pytest.raises(ProgrammingError)),
            (NONE_USER_ID, pytest.raises(AssertionError)),
        ]
    )
    async def test_select_stopped_trackers(
            self, user_id: int, db_session_fixture: AsyncSession, expectation: Any
    ) -> None:
        with expectation:
            res_fetchall = await select_stopped_trackers(
                user_id, db_session=db_session_fixture
            )
            assert res_fetchall

    @pytest.mark.parametrize(
        ['user_id', 'expectation'],
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            (ABSENT_IN_DB_USER_ID, pytest.raises(AssertionError)),
            (INVALID_USER_ID, pytest.raises(ProgrammingError)),
            (NONE_USER_ID, pytest.raises(AssertionError)),
        ]
    )
    async def test_get_report(
            self, user_id: int, db_session_fixture: AsyncSession, expectation: Any
    ) -> None:
        with expectation:
            res_fetchall = await select_weekly_trackers(
                user_id, db_session=db_session_fixture
            )
            assert res_fetchall

    @pytest.mark.parametrize(
        ['user_id', 'tracker_id', 'expectation'],
        [
            (MAIN_USER_ID, 1, does_not_raise()),
            (OTHER_USER_ID, 2, does_not_raise()),
            (MAIN_USER_ID, '1', pytest.raises(DBAPIError)),
            (INVALID_USER_ID, 1, pytest.raises(DBAPIError)),
            (MAIN_USER_ID, -1, pytest.raises(AssertionError)),
            (ABSENT_IN_DB_USER_ID, 1, pytest.raises(AssertionError)),
            (NONE_USER_ID, 1, pytest.raises(AssertionError)),
        ]
             )
    async def test_delete_tracker(
            self, db_session_fixture: AsyncSession, user_id: int, tracker_id: int,
            expectation: Any,
    ) -> None:
        with expectation:
            res_scalar_one_or_none = await delete_tracker(
                user_id, tracker_id, db_session=db_session_fixture
            )
            assert res_scalar_one_or_none == tracker_id
