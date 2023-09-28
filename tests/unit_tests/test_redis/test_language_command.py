import pytest
from redis.asyncio import Redis
from contextlib import nullcontext as does_not_raise

from cache.redis_language_commands import redis_hget_lang
from config import settings
from tests.unit_tests.utils import MAIN_USER_ID


@pytest.mark.asyncio
class TestRedisGetLang:
    @pytest.mark.parametrize(
        "user_id, local, expectation",
        [
            (MAIN_USER_ID, "ru", does_not_raise()),
            (MAIN_USER_ID, "en", does_not_raise()),
            (MAIN_USER_ID, None, does_not_raise()),
            (MAIN_USER_ID, settings.GLOBAL_LANG_CODE, does_not_raise()),
            (MAIN_USER_ID, settings.RU_LANG_CODE, does_not_raise()),
            (MAIN_USER_ID, settings.EN_LANG_CODE, does_not_raise()),
        ]
    )
    async def test_redis_hget_lang(self, user_id: int,  redis_cli: Redis, expectation, local: None | str):
        with expectation:
            lang = await redis_hget_lang(user_id, redis_cli, local)
            assert isinstance(lang, str)
            if local is None:
                assert lang == settings.GLOBAL_LANG_CODE
            else:
                assert lang == local

