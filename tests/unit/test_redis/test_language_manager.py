from typing import Any

import pytest
from redis.asyncio import Redis
from contextlib import nullcontext as does_not_raise

from cache.language_redis_manager import redis_hget_lang, redis_hset_lang
from config import settings
from tests.utils import MAIN_USER_ID, OTHER_USER_ID


@pytest.mark.asyncio
class TestLanguageManager:
    """
    Test suite for Redis-based language management.

    This test suite contains test methods for getting and setting user language
    preferences in a Redis cache.
    """

    @pytest.mark.parametrize(
        "user_id, local, expectation",
        [
            (MAIN_USER_ID, "ru", does_not_raise()),
            (OTHER_USER_ID, "en", does_not_raise()),
            (MAIN_USER_ID, None, does_not_raise()),
            (MAIN_USER_ID, settings.GLOBAL_LANG_CODE, does_not_raise()),
            (OTHER_USER_ID, settings.RU_LANG_CODE, does_not_raise()),
            (MAIN_USER_ID, settings.EN_LANG_CODE, does_not_raise()),
        ]
    )
    async def test_redis_hget_lang(self, user_id: int,  redis_cli: Redis,
                                   expectation: Any, local: None | str) -> None:
        """
        Test the 'redis_hget_lang' function for getting user language preferences.

        This test method verifies the behavior of the 'redis_hget_lang' function by
        attempting to retrieve user language preferences from the Redis cache.
        It checks if the returned language matches the expected language or the default
        language.

        :param user_id: int: The user ID for testing.
        :param redis_cli: Redis: An asynchronous Redis client.
        :param local: None | str: The expected user language preference.
        :param expectation: Any: An expectation for test outcome.

        :return: None
        """
        with expectation:
            lang = await redis_hget_lang(user_id, redis_cli, local)
            assert isinstance(lang, str)
            if local is None:
                assert lang == settings.GLOBAL_LANG_CODE
            else:
                assert lang == local

    @pytest.mark.parametrize(
        "user_id, local, expectation",
        [
            (OTHER_USER_ID, "ru", does_not_raise()),
            (MAIN_USER_ID, "en", does_not_raise()),
            (OTHER_USER_ID, None, pytest.raises(AssertionError)),
            (OTHER_USER_ID, settings.GLOBAL_LANG_CODE, does_not_raise()),
            (MAIN_USER_ID, settings.RU_LANG_CODE, does_not_raise()),
            (OTHER_USER_ID, settings.EN_LANG_CODE, does_not_raise()),
        ]
    )
    async def test_redis_hset_lang(self, user_id: int,  redis_cli: Redis,
                                   expectation: Any, local: bytes | str) -> None:
        """
        Test the 'redis_hset_lang' function for setting user language preferences.

        This test method verifies the behavior of the 'redis_hset_lang' function by
        attempting to set user language preferences in the Redis cache and then
        retrieving the language. It checks if the retrieved language matches the
        expected language.

        :param user_id: int: The user ID for testing.
        :param redis_cli: Redis: An asynchronous Redis client.
        :param local: bytes | str: The user language preference to be set.
        :param expectation: Any: An expectation for test outcome.

        :return: None
        """
        with expectation:
            await redis_hset_lang(user_id, redis_cli, local)
            lang = await redis_hget_lang(user_id, redis_cli)
            assert isinstance(lang, str)
            assert lang == local
