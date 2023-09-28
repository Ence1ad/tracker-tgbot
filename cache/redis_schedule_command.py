from redis.asyncio import Redis


async def _set_name(name: str = "users") -> str:
    """
    The _set_name function is a helper function that sets the name of the
        database table. It defaults to &quot;users&quot; if no argument is passed in.

    :param name: str: Define the name of the function
    :return: The name of the collection
    """
    return name


async def redis_sadd_user_id(user_id: int, redis_client: Redis) -> int:

    """
    The redis_sadd_user_id function adds a user_id to the set of users who have been
        sent a message.

    :param user_id: int: Set the user_id
    :param redis_client: Redis: Pass a redis client object to the function
    :return: 1 if adding the user id was successfully, 0 if not
    """
    name: str = await _set_name()
    return await redis_client.sadd(name, user_id)


async def is_redis_sismember_user(user_id: int, redis_client: Redis) -> bool | None:

    """
    The is_redis_sismember_user function checks if a user is in the Redis set.

    :param user_id: int: Get the user id of the user
    :param redis_client: Redis: Pass the redis client object to the function
    :return:True if the user id in the redis set, False if not
    """
    name: str = await _set_name()
    user_exists = await redis_client.sismember(name=name, value=str(user_id))
    return True if user_exists else False


async def redis_smembers_users(redis_client: Redis) -> set | None:

    """
    The redis_smembers_users function returns a set of all the users in the Redis database.

    :param redis_client: Redis: Pass the redis client object
    :return: A set of users
    """
    name: str = await _set_name()
    members = await redis_client.smembers(name=name)
    return members if members else None
