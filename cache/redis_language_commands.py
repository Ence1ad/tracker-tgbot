from redis.asyncio import Redis

from config import settings


def _set_name(name: str = "lang") -> str:
    """
    The _set_name function is a helper function that sets the name of the redis
        database table. It defaults to &quot;users&quot; if no argument is passed in.

    :param name: str: Define the name of the function
    :return: The name of the collection
    """
    return name


async def redis_hget_lang(user_id: int,  redis_client: Redis, local: str | None = None) -> str:
    """
    The redis_hget_lang function is a helper function that returns the language code of the user.
    If no language code is found in Redis, it will return the default global language code.

    :param user_id: int: Get the user's language from redis
    :param redis_client: Redis: Pass the redis client to the function
    :param local: None | str: Set the default language to english
    :return: The language code for the user
    """
    name = _set_name()
    lang_code: bytes | str = await redis_client.hget(name=name, key=str(user_id))
    if isinstance(lang_code, bytes):
        lang_code = lang_code.decode(encoding='utf-8')
        return lang_code
    if not lang_code and local is not None:
        return local
    else:
        return settings.EN_LANG_CODE


async def redis_hset_lang(user_id: int,  redis_client: Redis, lang_code: str | bytes) -> int:
    """
    The redis_hset_lang function is used to set the language code for a user.

    :param user_id: int: Specify the user id of the user
    :param redis_client: Redis: Pass the redis client object to the function
    :param lang_code: str | bytes: Specify the language code
    :return: The number of fields that were changed
    """
    if lang_code is not None:
        name = _set_name()
        return await redis_client.hset(name=name, key=str(user_id), value=lang_code)

