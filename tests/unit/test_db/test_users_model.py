import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError, DBAPIError

from db.models.user_model import UserModel
from db.operations.users_operations import create_user, delete_user
from tests.utils import MAIN_USER_ID, INVALID_USER_ID, OTHER_USER_ID


@pytest.mark.asyncio
class TestUsers:
    @pytest.mark.parametrize(
        "user_id, first_name, last_name, username, expectation",
        [
            (MAIN_USER_ID, 'Ivan', 'Ivanov', 'Rus', does_not_raise()),
            (MAIN_USER_ID, '', '', '', pytest.raises(IntegrityError)),
            (OTHER_USER_ID, 'Ivan', 'Ivanov', 'Rus', does_not_raise()),
            (1000000003, 'Ivan', 'Ivanov', None, does_not_raise()),
            (1000000004, 'Ivan', None, None, does_not_raise()),
            (1000000006, '', '', '', does_not_raise()),
            (INVALID_USER_ID, '', '', '', pytest.raises(IntegrityError)),
            ('abc', '', '', '', pytest.raises(DBAPIError)),
            (1000000007, 123, '', '', pytest.raises(DBAPIError)),
            (1000000008, '', 123, '', pytest.raises(DBAPIError)),
            (1000000009, '', '', 123, pytest.raises(DBAPIError)),
            (1000000010, 123, 123, 123, pytest.raises(DBAPIError)),
        ]
    )
    async def test_create_user(
            self,
            db_session_fixture: AsyncSession,
            user_id: int,
            first_name: str,
            last_name: str,
            username: str,
            expectation: does_not_raise
    ):
        with expectation:
            user_model = await create_user(user_id, first_name, last_name, username, db_session=db_session_fixture)
            assert isinstance(user_model, UserModel)
            assert user_model.user_id == user_id
            assert user_model.first_name == first_name
            assert user_model.last_name == last_name
            assert user_model.username == username

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID,  does_not_raise()),
            (MAIN_USER_ID, pytest.raises(AssertionError)),
            (OTHER_USER_ID,  does_not_raise()),
            (1000000004,  does_not_raise()),
            (1000000006,  does_not_raise()),
        ]
    )
    async def test_delete_user(
            self,
            db_session_fixture: AsyncSession,
            user_id: int,
            expectation: does_not_raise
    ):
        with expectation:
            result = await delete_user(user_id, db_session=db_session_fixture)
            assert isinstance(result, int)
            assert result == user_id

