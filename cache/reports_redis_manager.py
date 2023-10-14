import datetime
from datetime import date, time
from redis.asyncio import Redis


REPORT_PREFIX = 'is_report_need_update'


def set_redis_name(user_id: int, prefix: str = '') -> str:
    """
    Create name for redis data structure

    The _set_name function takes a user_id and an optional prefix,
    and returns the name of the key in Redis that will be used to store
    the user's data. The default prefix is 'user', so if you don't pass one,
    it'll use 'user:&lt;user_id&gt;' as the key.

    :param user_id: int: Set the user_id to an integer
    :param prefix: str: Set a prefix for the name of the user
    :return: A string, the name of the user
    """
    name = f"{prefix}:{user_id}"
    return name


async def redis_set_report_need_upd(user_id: int, redis_client: Redis, value: int):
    """
    The redis_set_report_need_upd function sets the value of a key in Redis.
    
    The value of this key determines whether or not a report needs to be updated.
    If it's set to 1, then it does need updating; if 0, then no update needed.
    
    :param user_id: int: Identify the user
    :param redis_client: Redis: Connect to the redis database
    :param value: int: Set the value of the key
    :return: A string, which is the status of the operation
    """
    if not isinstance(value, int):
        raise ValueError
    if value not in [0, 1]:
        raise ValueError

    name = set_redis_name(user_id, REPORT_PREFIX)
    res = await redis_client.set(name=name, value=value, keepttl=True)
    return res


async def redis_get_report_need_upd(user_id: int, redis_client: Redis):
    """
    The redis_get_report_need_upd function is used to get the value of a key in Redis.
    
    :param user_id: int: Set the name of the key in redis
    :param redis_client: Redis: Pass the redis client to the function
    :return: The value of the report_need_upd flag
    """
    name = set_redis_name(user_id, REPORT_PREFIX)
    res = await redis_client.get(name=name)
    return res


async def redis_expireat_end_of_week(user_id: int, redis_client: Redis) -> bool:
    """
    Set the expiration time of a Redis key for a given user to the end of the current week starting from Monday.

    :param user_id: int: Identify the user in Redis.
    :param redis_client: Redis: Pass the Redis client to the function.
    :return: True if the expiration time was set successfully, False if not.
    """
    today = date.today()

    # Calculate the start of the next week (Monday)
    days_until_monday = (7 - today.weekday()) % 7
    start_of_next_week = today + datetime.timedelta(days=days_until_monday)

    # Calculate the end of the week (Sunday)
    end_of_week = start_of_next_week + datetime.timedelta(days=6)

    # Set midnight time
    midnight_time = time.max
    # Set the expiration time to the end of the week (23:59:59 on Sunday)
    end_of_week_time = datetime.datetime.combine(end_of_week, midnight_time)

    return await redis_client.expireat(name=f"is_report_need_update:{user_id}", when=end_of_week_time, nx=True)