from redis.asyncio import Redis

from cache.redis_utils import set_redis_name
from config import settings

LANG_PREFIX = 'lang'


async def redis_hget_lang(user_id: int,  redis_client: Redis, local: str | None = None
                          ) -> str:
    """
    Retrieve the language code for a user from Redis.

    This function fetches the language code associated with a user from a Redis
    database. If no language code is found, it returns the default global language code
    or the provided local code.

    :param user_id: int: The unique identifier of the user.
    :param redis_client: Redis: An instance of a Redis client.
    :param local: str | None: An optional local language code (default is None).
    :return: str: The language code for the user or the local language code if
    specified.
    """
    lang_name: str = set_redis_name(user_id, LANG_PREFIX)
    lang_code: bytes | str = await redis_client.hget(name=lang_name, key=str(user_id))
    if isinstance(lang_code, bytes):
        lang_code = lang_code.decode(encoding='utf-8')
        return lang_code
    if not lang_code and local is not None:
        return local
    else:
        return settings.EN_LANG_CODE


async def redis_hset_lang(user_id: int,  redis_client: Redis, lang_code: str | bytes
                          ) -> int:
    """
    Set the language code for a user in Redis.

    This function is used to update the language code for a user in a Redis database.

    :param user_id: int: The unique identifier of the user.
    :param redis_client: Redis: An instance of a Redis client.
    :param lang_code: str | bytes: The language code to set for the user.
    :return: int: The number of fields that were changed (0 if no changes occurred).
    """
    lang_name: str = set_redis_name(user_id, LANG_PREFIX)
    return await redis_client.hset(name=lang_name, key=str(user_id),
                                   value=str(lang_code))
