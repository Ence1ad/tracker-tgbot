import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError, DBAPIError, ProgrammingError

from db.report.report_commands import get_report
from db.tracker.tracker_db_command import create_tracker, stop_tracker, delete_tracker, select_stopped_trackers


@pytest.mark.usefixtures('add_action')
@pytest.mark.asyncio
class TestTrackers:
    @pytest.mark.parametrize(
        "user_id, category_id, action_id, expectation",
        [
            (1111111111, 1, 1, does_not_raise()),
            (1111111111, 1, -1, pytest.raises(IntegrityError)),
            (1111111111, -1, 1, pytest.raises(IntegrityError)),
            (1111111111, 1, None, pytest.raises(IntegrityError)),
            (1111111111, None, 1, pytest.raises(IntegrityError)),
            (None, 1, 1, pytest.raises(IntegrityError)),
            (1111111111, '1', 1, pytest.raises(DBAPIError)),
            (1111111111, 1, '1', pytest.raises(DBAPIError)),
            ('1111111111', 1, 1, pytest.raises(DBAPIError)),
        ]
    )
    async def test_create_tracker(
            self,
            session: AsyncSession,
            user_id: int,
            action_id: int,
            category_id: int,
            expectation: does_not_raise,
    ):
        with expectation:
            tracker_obj = await create_tracker(
                user_id=user_id,
                action_id=action_id,
                category_id=category_id,
                # track_start=datetime.datetime.now(),
                db_session=session
            )
            assert tracker_obj.user_id == user_id
            # assert tracker_obj.track_end is None
            assert tracker_obj.duration is None

    # @pytest.mark.parametrize(
    #     "user_id, expectation",
    #     [
    #         (1111111111, does_not_raise()),
    #         (-1, pytest.raises(AssertionError)),
    #         ('1', pytest.raises(ProgrammingError)),
    #         (None, pytest.raises(AssertionError)),
    #     ]
    #          )
    # async def test_select_started_tracker(
    #         self,
    #         session: AsyncSession,
    #         user_id: int,
    #         expectation: does_not_raise,
    # ):
    #     with expectation:
    #         trackers_scalar_one_or_none = await select_started_tracker(user_id, db_session=session)
    #         assert trackers_scalar_one_or_none is not None

    @pytest.mark.parametrize(
        ['user_id', 'tracker_id', 'expectation'],
        [
            (1111111111, 1, does_not_raise()),
            (1111111111, '1', pytest.raises(DBAPIError)),
            ('1111111111', 1, pytest.raises(DBAPIError)),
            (1111111111, None, pytest.raises(AssertionError)),
            (1111111111, -1, pytest.raises(AssertionError)),
            (-1, 1, pytest.raises(AssertionError)),
            (None, 1, pytest.raises(AssertionError)),
        ]
             )
    async def test_stop_tracker(
            self,
            session: AsyncSession,
            user_id: int,
            tracker_id: int,
            expectation: does_not_raise,
    ):
        with expectation:
            duration_returning = await stop_tracker(user_id, tracker_id, db_session=session)
            assert duration_returning is not None

    @pytest.mark.parametrize(
        ['user_id', 'expectation'],
        [
            (1111111111, does_not_raise()),
            (-1, pytest.raises(AssertionError)),
            ('1', pytest.raises(ProgrammingError)),
            (None, pytest.raises(AssertionError)),
        ]
    )
    async def test_select_stopped_trackers(
            self,
            user_id: int,
            session: AsyncSession,
            expectation: does_not_raise
    ):
        with expectation:
            res_fetchall = await select_stopped_trackers(user_id, db_session=session)
            assert res_fetchall != []

    @pytest.mark.parametrize(
        ['user_id', 'expectation'],
        [
            (1111111111, does_not_raise()),
            (-1, pytest.raises(AssertionError)),
            ('1', pytest.raises(ProgrammingError)),
            (None, pytest.raises(AssertionError)),
        ]
    )
    async def test_get_report(
            self,
            user_id: int,
            session: async_sessionmaker[AsyncSession],
            expectation: does_not_raise
    ):
        with expectation:
            res_fetchall = await get_report(user_id, db_session=session)
            assert res_fetchall != []

    @pytest.mark.parametrize(
        ['user_id', 'tracker_id', 'expectation'],
        [
            (1111111111, 1, does_not_raise()),
            (1111111111, '1', pytest.raises(DBAPIError)),
            ('1111111111', 1, pytest.raises(DBAPIError)),
            (1111111111, None, pytest.raises(AssertionError)),
            (1111111111, -1, pytest.raises(AssertionError)),
            (-1, 1, pytest.raises(AssertionError)),
            (None, 1, pytest.raises(AssertionError)),
        ]
             )
    async def test_delete_tracker(
            self,
            session: AsyncSession,
            user_id: int,
            tracker_id: int,
            expectation: does_not_raise,
    ):
        with expectation:
            res_scalar_one_or_none = await delete_tracker(user_id, tracker_id, db_session=session)
            assert res_scalar_one_or_none is not None
