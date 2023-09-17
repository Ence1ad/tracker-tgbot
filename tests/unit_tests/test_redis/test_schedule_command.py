import pytest
from contextlib import nullcontext as does_not_raise

from redis import DataError
from redis.asyncio import Redis

from cache.redis_schedule_command import redis_sadd_user_id, is_redis_sismember_user, redis_smembers_users

USER_ID = 1111111111


@pytest.mark.asyncio
class TestRedisScheduleCommands:

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (USER_ID, does_not_raise()),
            (USER_ID, pytest.raises(AssertionError)),
            ('1111111111', pytest.raises(AssertionError)),
            ('12345', does_not_raise()),
            (memoryview(b'11'), does_not_raise()),
            ([1, 2, 3], pytest.raises(DataError)),
            (None, pytest.raises(DataError)),
        ]
    )
    @pytest.mark.asyncio
    async def test_redis_add_user_id(self, user_id: int, expectation: does_not_raise, redis_cli: Redis):
        with expectation:
            res: int = await redis_sadd_user_id(user_id, redis_client=redis_cli)
            assert isinstance(res, int) is True
            assert res == 1

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (USER_ID, does_not_raise()),
            ('1111111111', does_not_raise()),
            ('12345678', pytest.raises(AssertionError)),
            ([1, 2, 3], pytest.raises(AssertionError)),
            (None, pytest.raises(AssertionError)),
        ]
    )
    async def test_is_redis_sismember_user(self, user_id: int, expectation: does_not_raise, redis_cli: Redis):
        with expectation:
            res = await is_redis_sismember_user(user_id, redis_client=redis_cli)
            assert isinstance(res, bool) is True
            assert res is True

    @pytest.mark.parametrize(
        "expectation",
        [
            (does_not_raise()),
        ]
    )
    @pytest.mark.asyncio
    async def test_redis_smembers_users(self, expectation: does_not_raise, redis_cli: Redis):
        with expectation:
            res: set = await redis_smembers_users(redis_client=redis_cli)
            assert isinstance(res, set) is True
            assert res != set()
