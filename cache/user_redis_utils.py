from redis.asyncio import Redis

REDIS_SET_NAME: str = "users"


async def redis_sadd_user_id(user_id: int, redis_client: Redis) -> int:
    """
    The redis_sadd_user_id function adds a user_id to the set of users who have been
        sent a message.

    :param user_id: int: Set the user_id
    :param redis_client: Redis: Pass a redis client object to the function
    :return: 1 if adding the user id was successfully, 0 if not
    """
    return await redis_client.sadd(REDIS_SET_NAME, user_id)


async def redis_srem_user_id(user_id: int, redis_client: Redis) -> int:
    """
    The redis_srem_user_id function removes a user_id from the set of all users.

    :param user_id: int: Specify the user id of the user to remove from the set
    :param redis_client: Redis: Pass in a redis client object
    :return: 1 if removing the user id was successfully, 0 if not
    """
    return await redis_client.srem(REDIS_SET_NAME, user_id)


async def is_redis_sismember_user(user_id: int, redis_client: Redis) -> bool | None:
    """
    The is_redis_sismember_user function checks if a user is in the Redis set.

    :param user_id: int: Get the user id of the user
    :param redis_client: Redis: Pass the redis client object to the function
    :return:True if the user id in the redis set, False if not
    """
    user_exists = await redis_client.sismember(name=REDIS_SET_NAME, value=str(user_id))
    return True if user_exists else False


async def redis_smembers_users(redis_client: Redis) -> set | None:

    """
    The redis_smembers_users function returns a set of all the users in the Redis database.

    :param redis_client: Redis: Pass the redis client object
    :return: A set of users
    """
    members = await redis_client.smembers(name=REDIS_SET_NAME)
    return members if members else None
