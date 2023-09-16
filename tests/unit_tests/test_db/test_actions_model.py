import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError, DBAPIError, ProgrammingError

from db.actions.actions_db_commands import create_actions, select_category_actions, delete_action, update_action_name


@pytest.mark.asyncio
@pytest.mark.usefixtures("add_category")
class TestActions:
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
    async def test_create_action(
            self,
            session: async_sessionmaker[AsyncSession],
            user_id: int,
            category_id: int,
            action_name: str,
            expectation: does_not_raise,
    ):
        with expectation:
            action_obj = await create_actions(user_id, category_id=category_id, action_name=action_name,
                                              db_session=session)
            assert action_obj.action_name == action_name

    @pytest.mark.parametrize(
        "user_id, category_id, expectation",
        [
            (1111111111, 1, does_not_raise()),
            (1111111111, -1, pytest.raises(AssertionError)),
            (1111111111, '1', pytest.raises(ProgrammingError)),
            ('1111111111', 1, pytest.raises(ProgrammingError)),
            (1111111111, None, pytest.raises(AssertionError)),
            (None, 1, pytest.raises(AssertionError)),
            (10000000001, 1, pytest.raises(AssertionError)),

        ]
    )
    async def test_select_category_actions(
            self,
            session: async_sessionmaker[AsyncSession],
            user_id: int,
            category_id: int,
            expectation: does_not_raise,
    ):
        with expectation:
            actions_fetchall = await select_category_actions(user_id, category_id, db_session=session)
            assert len(actions_fetchall) > 0

    @pytest.mark.parametrize(
        "user_id, action_id, new_action_name, expectation",
        [
            (1111111111, 1, 'new_name', does_not_raise()),
            (1111111111, 1, 'user_cool_action_name', pytest.raises(DBAPIError)),  # name > 20 chars
            (1111111111, '1', 'new_name', pytest.raises(DBAPIError)),
            ('1111111111', 1, 'new_name', pytest.raises(DBAPIError)),
            (1111111111, 1, 123, pytest.raises(DBAPIError)),
            (1111111111, 1, '', pytest.raises(IntegrityError)),
            (1111111111, 1, None, pytest.raises(IntegrityError)),
            (1111111111, None, 'new_name', pytest.raises(AssertionError)),
            (1111111111, -1, 'new_name', pytest.raises(AssertionError)),
            (-1, 1, 'new_name', pytest.raises(AssertionError)),
            (None, 1, 'new_name', pytest.raises(AssertionError)),
        ]
    )
    async def test_update_action(
            self,
            session: async_sessionmaker[AsyncSession],
            user_id: int,
            action_id: int,
            new_action_name: str,
            expectation: does_not_raise
    ):
        with expectation:
            res_id_scalar_one_or_none = await update_action_name(user_id, action_id, new_action_name, session)
            assert res_id_scalar_one_or_none == 1

    @pytest.mark.parametrize(
        "user_id, action_id, expectation",
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
    async def test_delete_action(
            self,
            session: async_sessionmaker[AsyncSession],
            user_id: int,
            action_id: int,
            expectation: does_not_raise
    ):
        with expectation:
            res_id_scalar_one_or_none = await delete_action(user_id, action_id, session)
            assert res_id_scalar_one_or_none == 1
