import datetime

import pytest
from contextlib import nullcontext as does_not_raise

from redis.asyncio import Redis

from cache.redis_commands import redis_sadd_user_id, redis_incr_user_day_trackers, redis_decr_user_day_trackers, \
    redis_expireat_midnight
from redis.exceptions import DataError

USER_ID = 1111111111

@pytest.mark.parametrize(
    "user_id, expectation",
    [
        (1111111111, does_not_raise()),
        (1111111111, pytest.raises(AssertionError)),
        ('1111111111', pytest.raises(AssertionError)),
        ('', does_not_raise()),
        (memoryview(b'11'), does_not_raise()),
        ([1, 2, 3], pytest.raises(DataError)),
        (None, pytest.raises(DataError)),
    ]
)
@pytest.mark.asyncio
async def test_redis_add_user_id(user_id: int, expectation: does_not_raise, redis_cli: Redis):
    with expectation:
        res = await redis_sadd_user_id(user_id, redis_client=redis_cli)
        assert res == 1


@pytest.mark.parametrize(
    "user_id, expectation",
    [
        (1111111111, does_not_raise()),
        (1111111111, pytest.raises(AssertionError)),
    ]
)
@pytest.mark.asyncio
async def test_redis_incr_user_day_trackers(user_id: int, expectation: does_not_raise, redis_cli: Redis):
    with expectation:
        incr = await redis_incr_user_day_trackers(user_id, redis_cli)
        assert incr == 1

@pytest.mark.parametrize(
    "user_id, expectation",
    [
        (1111111111, does_not_raise()),
        (1111111111, pytest.raises(AssertionError)),
    ]
)
@pytest.mark.asyncio
async def test_redis_decr_user_day_trackers(user_id: int, expectation: does_not_raise, redis_cli: Redis):
    with expectation:
        decr = await redis_decr_user_day_trackers(user_id, redis_cli)
        assert decr == 1


@pytest.mark.parametrize(
    "user_id, expectation",
    [
        (1111111111, does_not_raise()),
        (1111111111, pytest.raises(AssertionError)),
    ]
)
@pytest.mark.asyncio
async def test_redis_expireat_midnight(user_id: int, expectation: does_not_raise, redis_cli: Redis):
    with expectation:
        day_time = datetime.datetime.now() + datetime.timedelta(microseconds=1)
        res = await redis_expireat_midnight(user_id, redis_cli, day_time=day_time.time())
        assert res is True

