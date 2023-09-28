from redis.asyncio import Redis

from config import settings


async def redis_hget_lang(user_id: int,  redis_client: Redis, local: None | str = None) -> str:
    """
    The redis_hget_lang function is a helper function that returns the language code of the user.
    If no language code is found in Redis, it will return the default global language code.

    :param user_id: int: Get the user's language from redis
    :param redis_client: Redis: Pass the redis client to the function
    :param local: None | str: Set the default language to english
    :return: The language code for the user
    """
    if local is None:
        local = settings.GLOBAL_LANG_CODE
    else:
        if local_bytes := await redis_client.hget(name='lang', key=str(user_id)):
            local = local_bytes.decode(encoding='utf-8')
    return local
