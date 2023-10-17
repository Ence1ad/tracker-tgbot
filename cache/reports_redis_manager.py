import datetime
from datetime import date, time

from redis.asyncio import Redis

from cache.redis_utils import set_redis_name

REPORT_PREFIX = 'is_report_need_update'


async def redis_set_report_need_upd(user_id: int, redis_client: Redis, value: int
                                    ) -> bool:
    """Set the flag indicating whether a report needs an update in Redis.

    :param user_id: int: The user's unique identifier.
    :param redis_client: Redis: The Redis client for data storage.
    :param value: int: The value to set (0 for no update needed, 1 for update needed).
    :raises ValueError: If the 'value' parameter is not an integer or is not 0 or 1.
    :return: bool: The result of the Redis set operation.
    """
    if not isinstance(value, int):
        raise ValueError
    if value not in [0, 1]:
        raise ValueError

    name: str = set_redis_name(user_id, REPORT_PREFIX)
    res: bool = await redis_client.set(name=name, value=value, keepttl=True)
    return res


async def redis_get_report_need_upd(user_id: int, redis_client: Redis) -> int:
    """Get the flag indicating whether a report needs an update from Redis.

    :param user_id: int: The user's unique identifier.
    :param redis_client: Redis: The Redis client for data storage.
    :return: int: The stored value of the flag (0 for no update needed,
     1 for update needed).
    """
    name: str = set_redis_name(user_id, REPORT_PREFIX)
    res: int = await redis_client.get(name=name)
    return res


async def redis_expireat_end_of_week(user_id: int, redis_client: Redis) -> bool:
    """Set a Redis key to expire at the end of the current week (Sunday at 23:59:59).

    :param user_id: int: The user's unique identifier.
    :param redis_client: Redis: The Redis client for data storage.
    :return: bool: The result of the Redis expireat operation.
    """
    today: date = date.today()

    # Calculate the start of the next week (Monday)
    days_until_monday: int = (7 - today.weekday()) % 7
    start_of_next_week: date = today + datetime.timedelta(days=days_until_monday)

    # Calculate the end of the week (Sunday)
    end_of_week: date = start_of_next_week + datetime.timedelta(days=6)

    # Set midnight time
    midnight_time: time = time.max
    # Set the expiration time to the end of the week (23:59:59 on Sunday)
    end_of_week_time: datetime.datetime = datetime.datetime.combine(end_of_week,
                                                                    midnight_time)
    name: str = set_redis_name(user_id, REPORT_PREFIX)
    res: bool = await redis_client.expireat(name=name, when=end_of_week_time, nx=True)
    return res
