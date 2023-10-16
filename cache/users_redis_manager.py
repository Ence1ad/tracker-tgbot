from redis.asyncio import Redis

REDIS_USERS_SET: str = "users"


async def redis_sadd_user_id(user_id: int, redis_client: Redis) -> int:
    """Add a user ID to a Redis set.

    This function adds a user's ID to a Redis set for tracking users who have been sent
    a message.

    :param user_id: int: The unique identifier of the user.
    :param redis_client: Redis: An instance of a Redis client.
    :return: int: 1 if the user ID was successfully added to the set, 0 if not.
    """
    return await redis_client.sadd(REDIS_USERS_SET, user_id)


async def redis_srem_user_id(user_id: int, redis_client: Redis) -> int:
    """Remove a user ID from a Redis set.

    This function removes a user's ID from a Redis set of users who have been sent
    a message.

    :param user_id: int: The unique identifier of the user to remove from the set.
    :param redis_client: Redis: An instance of a Redis client.
    :return: int: 1 if the user ID was successfully removed from the set, 0 if not.
    """
    return await redis_client.srem(REDIS_USERS_SET, user_id)


async def is_redis_sismember_user(user_id: int, redis_client: Redis) -> bool | None:
    """Check if a user ID exists in a Redis set.

    This function checks if a user's ID exists in a Redis set of users who have been
    sent a message.

    :param user_id: int: The unique identifier of the user to check.
    :param redis_client: Redis: An instance of a Redis client.
    :return: bool | None: True if the user ID exists in the set, False if not, or None
    if there was an error.
    """
    user_exists = await redis_client.sismember(name=REDIS_USERS_SET, value=str(user_id))
    return True if user_exists else False


async def redis_smembers_users(redis_client: Redis, set_name: str = REDIS_USERS_SET
                               ) -> set[str] | None:
    """Retrieve a set of all user IDs from a Redis set.

    This function retrieves a set of all user IDs from a Redis set of users who have
    been sent a message.

    :param set_name: str: Redis set name (default = REDIS_USERS_SET)
    :param redis_client: Redis: An instance of a Redis client.
    :return: set | None: A set of user IDs if available, or None if the set is empty or
    an error occurred.
    """
    members = await redis_client.smembers(name=set_name)
    return members if members else None
