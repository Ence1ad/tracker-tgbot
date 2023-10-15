import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from contextlib import nullcontext as does_not_raise
from sqlalchemy.exc import IntegrityError, DBAPIError

from db.models.user_model import UserModel
from db.operations.users_operations import create_user, delete_user
from tests.utils import MAIN_USER_ID, INVALID_USER_ID, OTHER_USER_ID


@pytest.mark.asyncio
class TestUsers:
    """
    Test suite for the User-related functionality.

    This test suite contains test methods for creating and deleting user records.
    """

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
        """
        Test the 'create_user' function for user creation.

        This test method verifies the behavior of the 'create_user' function by
        attempting to create a user record in the database. It checks if the created
        user model matches the expected user attributes.

        :param user_id: int: The user ID for testing.
        :param first_name: str: The user's first name.
        :param last_name: str: The user's last name.
        :param username: str: The user's username.
        :param expectation: does_not_raise: An expectation for test outcome.
        :param db_session_fixture: AsyncSession: A fixture for the database session.

        :return: None
        """
        with expectation:
            user_model = await create_user(user_id, first_name, last_name, username,
                                           db_session=db_session_fixture)
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
            (INVALID_USER_ID, pytest.raises(AssertionError)),
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
        """
        Test the 'delete_user' function for user deletion.

        This test method verifies the behavior of the 'delete_user' function by
        attempting to delete a user record from the database. It checks if the function
        returns the expected result and handles exceptions properly.

        :param user_id: int: The user ID for testing.
        :param expectation: does_not_raise: An expectation for test outcome.
        :param db_session_fixture: AsyncSession: A fixture for the database session.

        :return: None
        """
        with expectation:
            result = await delete_user(user_id, db_session=db_session_fixture)
            assert isinstance(result, int)
            assert result == user_id
