import datetime
from contextlib import nullcontext as does_not_raise
from types import NoneType
from typing import Any

import pytest
from redis.asyncio import Redis
from redis.exceptions import DataError

from cache.redis_utils import set_redis_name
from cache.trackers_redis_manager import redis_hmset_create_tracker, \
    redis_hget_tracker_data, is_redis_hexists_tracker, redis_hgetall_started_tracker, \
    redis_upd_tracker, redis_delete_tracker, redis_decr_user_day_trackers, \
    redis_expireat_midnight, redis_incr_user_day_trackers,\
    redis_get_user_day_trackers, TRACKER_CNT_PREFIX
from tests.utils import MAIN_USER_ID, NONE_USER_ID, OTHER_USER_ID,\
    ABSENT_IN_DB_USER_ID, INVALID_USER_ID


@pytest.mark.asyncio
class TestRedisTrackerCommands:

    @pytest.mark.parametrize(
        "user_id, tracker_id, action_id, action_name, category_id, category_name,"
        " expectation",
        [
            (MAIN_USER_ID, 1, 1, "user_act", 1, "user_cat", does_not_raise()),
            (OTHER_USER_ID, 2, 2, "other_user_act", 2, "other_user_cat",
             does_not_raise()),

            (MAIN_USER_ID, 1, 1, "user_act", 1, "user_cat",
             pytest.raises(AssertionError)),
            (12345, 2, 1, "other_act", 1, "other_cat", does_not_raise()),
            (NONE_USER_ID, 1, 1, "user_act", 1, "user_cat",
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, None, 1, "user_act", 1, "user_cat",
             pytest.raises(DataError)),
            (MAIN_USER_ID, 1, None, "user_act", 1, "user_cat",
             pytest.raises(DataError)),
            (MAIN_USER_ID, 1, 1, None, 1, "user_cat", pytest.raises(DataError)),
            (MAIN_USER_ID, 1, 1, "user_act", None, "user_cat",
             pytest.raises(DataError)),
            (MAIN_USER_ID, 1, 1, "user_act", 1, None, pytest.raises(DataError)),
            (MAIN_USER_ID, 'str', 1, "user_act", 1, "user_cat",
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, 1, 'str', "user_act", 1, "user_cat",
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, 1, 1, 1, 1, "user_cat", pytest.raises(AssertionError)),
            (MAIN_USER_ID, 1, 1, "user_act", 'str', "user_cat",
             pytest.raises(AssertionError)),
            (MAIN_USER_ID, 1, 1, "user_act", 1, 1, pytest.raises(AssertionError)),
        ]
    )
    async def test_redis_hmset_create_tracker(
            self, user_id: int, tracker_id: str, action_id: int, action_name: str,
            category_id: int, category_name: str, redis_cli: Redis, expectation: Any
    ) -> None:
        with expectation:
            res: int | None = await redis_hmset_create_tracker(
                user_id, tracker_id, action_id, action_name, category_id,
                category_name, redis_client=redis_cli
            )
            assert isinstance(res, int | NoneType)
            assert res == 6

    @pytest.mark.parametrize(
        "user_id, key, expectation",
        [
            (MAIN_USER_ID, "tracker_id", does_not_raise()),
            (OTHER_USER_ID, "action_id", does_not_raise()),
            (MAIN_USER_ID, "action_name", does_not_raise()),
            (OTHER_USER_ID, "category_id", does_not_raise()),
            (MAIN_USER_ID, "category_name", does_not_raise()),
            (OTHER_USER_ID, "start_time", does_not_raise()),
            (MAIN_USER_ID, "", pytest.raises(AssertionError)),
            (MAIN_USER_ID, 12345, pytest.raises(AssertionError)),
            (MAIN_USER_ID, None, pytest.raises(DataError)),
            (OTHER_USER_ID, set(), pytest.raises(DataError)),
        ]
    )
    async def test_redis_hget_tracker_data(self, user_id: int, key: str,
                                           redis_cli: Redis, expectation: Any) -> None:
        with expectation:
            res = await redis_hget_tracker_data(user_id, key=key,
                                                redis_client=redis_cli)
            assert isinstance(res,  bytes | NoneType)
            assert res

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            (NONE_USER_ID, pytest.raises(AssertionError)),
            (ABSENT_IN_DB_USER_ID, pytest.raises(AssertionError)),
            (INVALID_USER_ID, pytest.raises(AssertionError)),

        ]
    )
    async def test_is_redis_hexists_tracker(self, user_id: int, expectation: Any,
                                            redis_cli: Redis) -> None:
        with expectation:
            res: bool = await is_redis_hexists_tracker(user_id, redis_client=redis_cli)
            assert isinstance(res, bool)
            assert res

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            (NONE_USER_ID, pytest.raises(AssertionError)),
            (ABSENT_IN_DB_USER_ID, pytest.raises(AssertionError)),
            (INVALID_USER_ID, pytest.raises(AssertionError))
        ]
    )
    async def test_redis_hgetall_started_tracker(self, user_id: int, expectation: Any,
                                                 redis_cli: Redis) -> None:
        with expectation:
            res = await redis_hgetall_started_tracker(user_id, redis_client=redis_cli)
            assert isinstance(res, dict | NoneType)
            assert res.get(b'tracker_id')

    @pytest.mark.parametrize(
        "user_id, action_name, category_name, expectation",
        [
            (MAIN_USER_ID, "user_act", "user_cat", does_not_raise()),
            (MAIN_USER_ID, "my_act", "my_cat", does_not_raise()),
            (OTHER_USER_ID, "other_user_act", "other_user_cat", does_not_raise()),
            (NONE_USER_ID,  "user_act", "user_cat", pytest.raises(AssertionError)),
        ]
    )
    async def test_redis_upd_tracker(
            self, user_id: int, action_name: str, category_name: str, redis_cli: Redis,
            expectation: Any
    ) -> None:
        with expectation:
            res: int | None = await redis_upd_tracker(
                user_id=user_id, action_name=action_name, category_name=category_name,
                redis_client=redis_cli
            )
            assert isinstance(res, int)
            assert res == 0

    @pytest.mark.parametrize(
        "user_id, expectation",
        [

            (MAIN_USER_ID, does_not_raise()),
            (NONE_USER_ID, pytest.raises(AssertionError)),
            (ABSENT_IN_DB_USER_ID, pytest.raises(AssertionError)),
            (INVALID_USER_ID, pytest.raises(AssertionError)),

        ]
    )
    async def test_redis_delete_tracker(self, user_id: int, expectation: Any,
                                        redis_cli: Redis) -> None:
        with expectation:
            res: int | None = await redis_delete_tracker(user_id,
                                                         redis_client=redis_cli)
            assert isinstance(res, int)
            assert res == 1

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
        ]
    )
    async def test_redis_incr_user_day_trackers(self, user_id: int, expectation: Any,
                                                redis_cli: Redis) -> None:
        with expectation:
            name = set_redis_name(user_id, TRACKER_CNT_PREFIX)
            before = await redis_cli.get(name)
            incr = await redis_incr_user_day_trackers(user_id, redis_cli)
            after = await redis_cli.get(name)
            assert isinstance(incr, int)
            assert before != after

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            (NONE_USER_ID, pytest.raises(AssertionError)),
            (INVALID_USER_ID, pytest.raises(AssertionError)),
        ]
    )
    async def test_redis_get_user_day_trackers(self, user_id: int, expectation: Any,
                                               redis_cli: Redis) -> None:
        with expectation:
            res = await redis_get_user_day_trackers(user_id, redis_cli)
            assert isinstance(res, bytes)
            assert res

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            (ABSENT_IN_DB_USER_ID, pytest.raises(AssertionError)),
        ]
    )
    async def test_redis_decr_user_day_trackers(self, user_id: int, expectation: Any,
                                                redis_cli: Redis) -> None:
        with expectation:
            name = set_redis_name(user_id, TRACKER_CNT_PREFIX)
            before = await redis_cli.get(name)
            decr = await redis_decr_user_day_trackers(user_id, redis_cli)
            after = await redis_cli.get(name)
            assert isinstance(decr, int)
            assert before != after

    @pytest.mark.parametrize(
        "user_id, sec, expectation",
        [
            (MAIN_USER_ID, None, does_not_raise()),  # ttl - time.max
            (MAIN_USER_ID, 100, pytest.raises(AssertionError)),  # nx = True
            (OTHER_USER_ID, 200,  does_not_raise()),  # ttl - 200 sec
        ]
    )
    async def test_redis_expireat_midnight(self, user_id: int, expectation: Any, sec,
                                           redis_cli: Redis) -> None:
        with expectation:
            if sec:
                dt = datetime.datetime.now() + datetime.timedelta(seconds=sec)
                day_time = dt.time()
            else:
                day_time = None
            res = await redis_expireat_midnight(user_id, redis_cli, day_time=day_time)
            assert isinstance(res, bool)
            assert res

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            (NONE_USER_ID, does_not_raise()),
            (INVALID_USER_ID, does_not_raise()),
        ]
    )
    async def test_set_redis_name(self, user_id: int, expectation: Any) -> None:
        with expectation:
            res = set_redis_name(user_id)
            assert isinstance(res, str)
            assert res == set_redis_name(user_id)
