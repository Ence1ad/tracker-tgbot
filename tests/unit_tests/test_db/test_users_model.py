import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError, DBAPIError

from db.users.user_model import UserModel
from db.users.users_commands import create_user


@pytest.mark.usefixtures('add_user')
@pytest.mark.asyncio
class TestUsers:
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
    async def test_create_user(
            self,
            session: async_sessionmaker[AsyncSession],
            user_id: int,
            first_name: str,
            last_name: str,
            username: str,
            expectation: does_not_raise
    ):
        with expectation:
            user_model: UserModel = await create_user(user_id, first_name, last_name, username, db_session=session)
            assert user_model.user_id == user_id
