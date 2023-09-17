from redis.asyncio import Redis


async def _set_name(name: str = "users") -> str:
    """
    Auxiliary function that set up the redis set name

    :param name: Redis set name
    :return: Redis set name
    """
    return name


async def redis_sadd_user_id(user_id: int, redis_client: Redis) -> int:
    """
    Add the user id to the redis set

    :param user_id: Telegram user id derived from call or message
    :param redis_client: Async Redis class derived from middleware
    :return:  1 if adding the user id was successfully, 0 if not
    """
    name: str = await _set_name()
    return await redis_client.sadd(name, user_id)


async def is_redis_sismember_user(user_id: int, redis_client: Redis) -> bool | None:
    """
    Checks the redis set for the presence of a user id

    :param user_id: Telegram user id derived from call or message
    :param redis_client: Async Redis class derived from middleware
    :return: True if the user id exists in the redis set, False if not
    """
    name: str = await _set_name()
    user_exists = await redis_client.sismember(name=name, value=str(user_id))
    return True if user_exists else False


async def redis_smembers_users(redis_client: Redis) -> set | None:
    """
    Get all user ids from the redis set

    :param redis_client: Async Redis class derived from middleware
    :return: A set of the user ids or none
    """
    name: str = await _set_name()
    members = await redis_client.smembers(name=name)
    return members if members else None
