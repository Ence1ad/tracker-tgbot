from typing import Any

import pytest
from contextlib import nullcontext as does_not_raise

from redis import DataError
from redis.asyncio import Redis

from cache.users_redis_manager import redis_sadd_user_id, is_redis_sismember_user, \
    redis_smembers_users, redis_srem_user_id, REDIS_USERS_SET
from tests.utils import MAIN_USER_ID, OTHER_USER_ID, NONE_USER_ID


@pytest.mark.asyncio
class TestUsersManager:
    """
    Test suite for user management functions related to Redis.

    This test suite contains test methods for adding, checking, and removing user IDs
    from Redis, including edge cases.
    """

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (MAIN_USER_ID, pytest.raises(AssertionError)),
            (OTHER_USER_ID, does_not_raise()),
            (memoryview(b'11'), does_not_raise()),
            ([1, 2, 3], pytest.raises(DataError)),
            (NONE_USER_ID, pytest.raises(DataError)),
        ]
    )
    async def test_redis_add_user_id(self, user_id: int, expectation: Any,
                                     redis_cli: Redis) -> None:
        """
        Test the 'redis_sadd_user_id' function for adding user IDs to a Redis set.

        This test method verifies the behavior of the 'redis_sadd_user_id' function by
        attempting to add a user ID to a Redis set. It checks if the function returns
        the expected result and handles exceptions properly.

        :param user_id: int: The user ID for testing.
        :param expectation: Any: An expectation for test outcome.
        :param redis_cli: Redis: A Redis client for testing.

        :return: None
        """
        with expectation:
            res: int = await redis_sadd_user_id(user_id, redis_client=redis_cli)
            assert isinstance(res, int)
            assert res == 1

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            ('12345678', pytest.raises(AssertionError)),
            ([1, 2, 3], pytest.raises(AssertionError)),
            (NONE_USER_ID, pytest.raises(AssertionError)),
        ]
    )
    async def test_is_redis_sismember_user(self, user_id: int, redis_cli: Redis,
                                           expectation: Any) -> None:
        """
        Test the 'is_redis_sismember_user' function.

        This test method verifies the behavior of the 'is_redis_sismember_user'
        function by checking if a user ID exists in a Redis set. It checks if the
        function returns the expected result and handles exceptions properly.

        :param user_id: int: The user ID for testing.
        :param expectation: Any: An expectation for test outcome.
        :param redis_cli: Redis: A Redis client for testing.

        :return: None
        """
        with expectation:
            res = await is_redis_sismember_user(user_id, redis_client=redis_cli)
            assert isinstance(res, bool)
            assert res

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            ('12345678', pytest.raises(AssertionError)),
            ([1, 2, 3], pytest.raises(DataError)),
            (NONE_USER_ID, pytest.raises(DataError)),
        ]
    )
    async def test_redis_srem_user_id(self, user_id: int, expectation: Any,
                                      redis_cli: Redis) -> None:
        """
        Test the 'redis_srem_user_id' function for removing a user ID from a Redis set.

        This test method verifies the behavior of the 'redis_srem_user_id' function by
        attempting to remove a user ID from a Redis set. It checks if the function
        returns the expected result and handles exceptions properly.

        :param user_id: int: The user ID for testing.
        :param expectation: Any: An expectation for test outcome.
        :param redis_cli: Redis: A Redis client for testing.

        :return: None
        """
        with expectation:
            res = await redis_srem_user_id(user_id, redis_client=redis_cli)
            assert isinstance(res, int)
            assert res

    @pytest.mark.parametrize(
        "set_name, expectation",
        [
            (REDIS_USERS_SET, does_not_raise()),
            ('not exist name', does_not_raise()),
        ]
    )
    async def test_redis_smembers_users(self, expectation: Any,
                                        set_name: str, redis_cli: Redis) -> None:
        """
        Test the 'redis_smembers_users' function.

        This test method verifies the behavior of the 'redis_smembers_users' function
        by retrieving all user IDs from a Redis set. It checks if the function returns
        the expected result and handles exceptions properly.

        :param expectation: Any: An expectation for test outcome.
        :param redis_cli: Redis: A Redis client for testing.

        :return: None
        """
        with expectation:
            res: set[str] | None = await redis_smembers_users(redis_client=redis_cli)
            assert isinstance(res, (set | None))
            assert res
