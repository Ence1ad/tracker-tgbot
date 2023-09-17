import datetime
from types import NoneType

import pytest
from contextlib import nullcontext as does_not_raise

from redis.asyncio import Redis

from cache.redis_tracker_commands import redis_hmset_tracker_data, \
    redis_hget_tracker_data, is_redis_tracker_exist, redis_hgetall_started_tracker, redis_upd_tracker, \
    redis_delete_tracker, redis_decr_user_day_trackers, redis_expireat_midnight, redis_incr_user_day_trackers
from redis.exceptions import DataError

USER_ID = 1111111111


@pytest.mark.asyncio
class TestRedisTrackerCommands:
    @pytest.mark.parametrize(
        "user_id, tracker_id, action_id, action_name, category_id, category_name, expectation",
        [
            (USER_ID, 1, 1, "user_act", 1, "user_cat", does_not_raise()),
            (USER_ID, 1, 1, "user_act", 1, "user_cat", pytest.raises(AssertionError)),
            (12345, 2, 1, "other_act", 1, "other_cat", does_not_raise()),
            (None, 1, 1, "user_act", 1, "user_cat", pytest.raises(DataError)),
            (USER_ID, None, 1, "user_act", 1, "user_cat", pytest.raises(DataError)),
            (USER_ID, 1, None, "user_act", 1, "user_cat", pytest.raises(DataError)),
            (USER_ID, 1, 1, None, 1, "user_cat", pytest.raises(DataError)),
            (USER_ID, 1, 1, "user_act", None, "user_cat", pytest.raises(DataError)),
            (USER_ID, 1, 1, "user_act", 1, None, pytest.raises(DataError)),
            (USER_ID, 'str', 1, "user_act", 1, "user_cat", pytest.raises(AssertionError)),
            (USER_ID, 1, 'str', "user_act", 1, "user_cat", pytest.raises(AssertionError)),
            (USER_ID, 1, 1, 1, 1, "user_cat", pytest.raises(AssertionError)),
            (USER_ID, 1, 1, "user_act", 'str', "user_cat", pytest.raises(AssertionError)),
            (USER_ID, 1, 1, "user_act", 1, 1, pytest.raises(AssertionError)),
        ]
    )
    async def test_redis_hmset_tracker_data(
            self, user_id: int, tracker_id: str, action_id: int, action_name: str,
            category_id: int, category_name: str, redis_cli: Redis, expectation: does_not_raise
    ):
        with expectation:
            res: int = await redis_hmset_tracker_data(user_id, tracker_id, action_id, action_name, category_id,
                                                      category_name, redis_client=redis_cli)
            assert isinstance(res, int) is True
            assert res == 6

    @pytest.mark.parametrize(
        "user_id, key, expectation",
        [
            (USER_ID, "tracker_id", does_not_raise()),
            (USER_ID, "action_id", does_not_raise()),
            (USER_ID, "action_name", does_not_raise()),
            (USER_ID, "category_id", does_not_raise()),
            (12345, "category_name", does_not_raise()),
            (12345, "start_time", does_not_raise()),
            (USER_ID, "", does_not_raise()),
            (USER_ID, 12345, does_not_raise()),
            (USER_ID, None, pytest.raises(DataError)),
            (USER_ID, set(), pytest.raises(DataError)),
        ]
    )
    async def test_redis_hget_tracker_data(self, user_id: int, key: str, redis_cli: Redis, expectation: does_not_raise):
        with expectation:
            res: bytes = await redis_hget_tracker_data(user_id, key=key, redis_client=redis_cli)
            data: dict = await redis_hgetall_started_tracker(user_id, redis_client=redis_cli)
            assert isinstance(res,  (bytes, NoneType)) is True
            assert res in data.values() or res is None

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (USER_ID, does_not_raise()),
            (None, pytest.raises(AssertionError)),
            (1, pytest.raises(AssertionError)),
            ('str', pytest.raises(AssertionError)),

        ]
    )
    async def test_is_redis_tracker_exist(self, user_id, expectation: does_not_raise, redis_cli: Redis):
        with expectation:
            res: bool = await is_redis_tracker_exist(user_id, redis_client=redis_cli)
            assert isinstance(res, bool) is True
            assert res is True

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (USER_ID, does_not_raise()),
            (None, pytest.raises(AssertionError)),
            (1, pytest.raises(AssertionError)),
            ('str', pytest.raises(AssertionError)),

        ]
    )
    async def test_redis_hgetall_started_tracker(self, user_id, expectation: does_not_raise, redis_cli: Redis):
        with expectation:
            res: dict = await redis_hgetall_started_tracker(user_id, redis_client=redis_cli)
            assert isinstance(res, (dict, NoneType)) is True
            assert res.get(b'tracker_id') == b'1'

    @pytest.mark.parametrize(
        "user_id, action_name, category_name, expectation",
        [
            (USER_ID, "user_act", "user_cat", does_not_raise()),
            (USER_ID, "my_act", "my_cat", does_not_raise()),
            (None,  "user_act", "user_cat", pytest.raises(AssertionError)),
            (USER_ID, "", "user_cat", pytest.raises(AssertionError)),
            (USER_ID, "user_act", "", pytest.raises(AssertionError)),
            (USER_ID, None, "user_cat", pytest.raises(AssertionError)),
            (USER_ID, "user_act", None, pytest.raises(AssertionError)),

        ]
    )
    async def test_redis_upd_tracker(
            self, user_id: int, action_name: str, category_name: str, redis_cli: Redis, expectation: does_not_raise
    ):
        with expectation:
            res: int = await redis_upd_tracker(user_id=user_id, action_name=action_name, category_name=category_name,
                                               redis_client=redis_cli)
            get_all: dict = await redis_hgetall_started_tracker(user_id=user_id, redis_client=redis_cli)
            assert isinstance(res, int) is True
            assert res == 0
            assert get_all.get(b'action_name').decode(encoding='utf-8') == action_name
            assert get_all.get(b'category_name').decode(encoding='utf-8') == category_name

    @pytest.mark.parametrize(
        "user_id, expectation",
        [

            (USER_ID, does_not_raise()),
            (None, pytest.raises(AssertionError)),
            (1, pytest.raises(AssertionError)),
            ('str', pytest.raises(AssertionError)),

        ]
    )
    async def test_redis_delete_tracker(self, user_id, expectation: does_not_raise, redis_cli: Redis):
        with expectation:
            res: int = await redis_delete_tracker(user_id, redis_client=redis_cli)
            print(res)
            assert isinstance(res, int) is True
            assert res == 1

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (USER_ID, does_not_raise()),
            (USER_ID, pytest.raises(AssertionError)),
        ]
    )
    async def test_redis_incr_user_day_trackers(self, user_id: int, expectation: does_not_raise, redis_cli: Redis):
        with expectation:
            incr = await redis_incr_user_day_trackers(user_id, redis_cli)
            assert incr == 1

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (USER_ID, does_not_raise()),
            (USER_ID, pytest.raises(AssertionError)),
        ]
    )
    async def test_redis_decr_user_day_trackers(self, user_id: int, expectation: does_not_raise, redis_cli: Redis):
        with expectation:
            decr = await redis_decr_user_day_trackers(user_id, redis_cli)
            assert decr == 1

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (USER_ID, does_not_raise()),
            (USER_ID, pytest.raises(AssertionError)),
        ]
    )
    async def test_redis_expireat_midnight(self, user_id: int, expectation: does_not_raise, redis_cli: Redis):
        with expectation:
            day_time = datetime.datetime.now() + datetime.timedelta(microseconds=1)
            res = await redis_expireat_midnight(user_id, redis_cli, day_time=day_time.time())
            assert res is True
