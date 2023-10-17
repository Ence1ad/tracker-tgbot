from contextlib import nullcontext as does_not_raise
from typing import Any

import pytest
from redis.asyncio import Redis

from cache.reports_redis_manager import redis_get_report_need_upd,\
    redis_set_report_need_upd, redis_expireat_end_of_week, REPORT_PREFIX
from cache.redis_utils import set_redis_name
from tests.utils import MAIN_USER_ID, OTHER_USER_ID


@pytest.mark.asyncio
class TestRedisTrackerCommands:

    @pytest.mark.parametrize(
        "user_id, value, expectation",
        [
            (MAIN_USER_ID, 0, does_not_raise()),
            (MAIN_USER_ID, 1, does_not_raise()),
            (OTHER_USER_ID, 1, does_not_raise()),
            (MAIN_USER_ID, '0', pytest.raises(ValueError)),
            (MAIN_USER_ID, -1, pytest.raises(ValueError)),
        ]
    )
    async def test_redis_set_report_need_upd(
            self, user_id: int, value: int, expectation: Any, redis_cli: Redis
    ) -> None:
        with expectation:
            res: bool = await redis_set_report_need_upd(user_id, redis_cli, value=value)
            assert isinstance(res, bool)
            assert res

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            (None, pytest.raises(AssertionError)),
            ('str', pytest.raises(AssertionError)),
        ]
    )
    async def test_redis_get_report_need_upd(self, user_id: int, expectation: Any,
                                             redis_cli: Redis) -> None:
        with expectation:
            res = await redis_get_report_need_upd(user_id, redis_cli)
            assert isinstance(res, bytes)
            assert int(res) in [0, 1]

    @pytest.mark.parametrize(
        "user_id, expectation",
        [
            (MAIN_USER_ID, does_not_raise()),
            (OTHER_USER_ID, does_not_raise()),
            (MAIN_USER_ID, pytest.raises(AssertionError)),
        ]
    )
    async def test_redis_expireat_end_of_week(
            self, user_id: int, expectation: Any, redis_cli: Redis
    ) -> None:
        await redis_set_report_need_upd(user_id, redis_cli, value=1)
        with expectation:
            res = await redis_expireat_end_of_week(user_id, redis_cli)
            val_with_ttl = set_redis_name(user_id, prefix=REPORT_PREFIX)
            assert await redis_cli.ttl(val_with_ttl) > 0
            assert isinstance(res, bool)
            assert res
