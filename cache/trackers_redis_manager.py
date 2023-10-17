import datetime
from datetime import datetime as dt, time, date
from typing import Any

from redis.asyncio import Redis

from cache.redis_utils import set_redis_name

TRACKER_PREFIX = 'tracker'
TRACKER_CNT_PREFIX = 'tracker_cnt'


async def redis_hmset_create_tracker(
        user_id: int, tracker_id: int | str, action_id: int, action_name: str,
        category_id: int, category_name: str, redis_client: Redis
) -> Any | None:
    """Create a new tracker in the Redis store.

    :param user_id: int: The unique identifier of the user.
    :param tracker_id: int | str: The unique identifier of the tracker.
    :param action_id: int: The unique identifier of the action associated with the
    tracker.
    :param action_name: str: The name of the action.
    :param category_id: int: The unique identifier of the category associated with the
    tracker.
    :param category_name: str: The name of the category.
    :param redis_client: Redis: The Redis client.
    :return: Any: Returns the number of fields that were added.
    """
    if user_id is not None:
        call_date: dt = dt.now()
        tracker_name: str = set_redis_name(user_id, TRACKER_PREFIX)
        res = await redis_client.hset(
            name=tracker_name,
            mapping={
                "start_time": str(call_date),
                "tracker_id": tracker_id,
                "action_id": action_id,
                "action_name": action_name,
                "category_id": category_id,
                "category_name": category_name
            }
        )
        return res
    return None


async def redis_hget_tracker_data(user_id: int, redis_client: Redis, key: str
                                  ) -> bytes | None:
    """Retrieve data from a tracker in the Redis store.

    :param user_id: int: The unique identifier of the user.
    :param redis_client: Redis: The Redis client.
    :param key: str: The key of the data to retrieve.
    :return: bytes or None: The data retrieved from Redis, or None if not found.
    """
    tracker_name: str = set_redis_name(user_id, TRACKER_PREFIX)
    res = await redis_client.hget(name=tracker_name, key=key)
    return res if res else None


async def is_redis_hexists_tracker(user_id: int, redis_client: Redis) -> bool:
    """Check if a tracker exists in the Redis store.

    :param redis_client: int | str: The unique identifier of the user or tracker.
    :param user_id: Redis: The Redis client.
    :return: bool: True if the tracker exists, False otherwise.
    """
    tracker_name: str = set_redis_name(user_id, TRACKER_PREFIX)
    tracker_exists = await redis_client.hexists(tracker_name, "start_time")
    return True if tracker_exists else False


async def redis_hgetall_started_tracker(user_id: int, redis_client: Redis
                                        ) -> dict[Any, Any] | None:
    """Retrieve all data from a started tracker in the Redis store.

    :param user_id: int: The unique identifier of the user.
    :param redis_client: Redis: The Redis client.
    :return: dict[Any: Any] or None: A dictionary containing all data from the
    tracker, or None if not found.
    """
    tracker_name: str = set_redis_name(user_id, TRACKER_PREFIX)
    return await redis_client.hgetall(tracker_name)


async def redis_upd_tracker(
        user_id: int, redis_client: Redis, action_name: str | None = None,
        category_name: str | None = None
) -> int | None:
    """Update tracker data in the Redis store.

    :param user_id: int: The unique identifier of the user.
    :param redis_client: Redis: The Redis client.
    :param action_name: str, optional: The new action name (default: None).
    :param category_name: str, optional: The new category name (default: None).
    :return: int: Returns the number of fields that were added
    """
    tracker_name: str = set_redis_name(user_id, TRACKER_PREFIX)
    tracker_data = await redis_client.hgetall(tracker_name)
    if tracker_data:
        res = await redis_hmset_create_tracker(
            user_id, redis_client=redis_client,
            tracker_id=tracker_data[b'tracker_id'],
            action_id=tracker_data[b'action_id'],
            action_name=action_name or tracker_data[b'action_name'],
            category_id=tracker_data[b'category_id'],
            category_name=category_name or tracker_data[b'category_name'],
        )
        return res
    return None


async def redis_delete_tracker(user_id: int, redis_client: Redis) -> int | None:
    """Delete a tracker from the Redis store.

    :param user_id: int: The unique identifier of the user.
    :param redis_client: Redis: The Redis client.
    :return: int or None: The result of the Redis operation (1 if successful,
    None otherwise).
    """
    tracker_name: str = set_redis_name(user_id, TRACKER_PREFIX)
    if await is_redis_hexists_tracker(user_id, redis_client):
        res: int = await redis_client.delete(tracker_name)
        return res
    return None


async def redis_incr_user_day_trackers(user_id: int, redis_client: Redis) -> Any:
    """Increment the user's daily tracker count in Redis.

    :param user_id: int: The unique identifier of the user.
    :param redis_client: Redis: The Redis client.
    :return: int: The updated user's daily tracker count.
    """
    tracker_cnt_name: str = set_redis_name(user_id, TRACKER_CNT_PREFIX)
    return await redis_client.incr(name=tracker_cnt_name, amount=1)


async def redis_decr_user_day_trackers(user_id: int, redis_client: Redis) -> Any | None:
    """Decrease the count of the user's daily trackers in Redis.

    :param user_id: int: The user's unique identifier.
    :param redis_client: Redis: The Redis client for data storage.
    :return: Any: The new count of daily trackers after decrement.
    """
    user_tracker_cnt = await redis_get_user_day_trackers(user_id, redis_client)
    if user_tracker_cnt and (int(user_tracker_cnt) > 0):
        tracker_cnt_name: str = set_redis_name(user_id, TRACKER_CNT_PREFIX)
        return await redis_client.decr(name=tracker_cnt_name, amount=1)
    return None


async def redis_get_user_day_trackers(user_id: int, redis_client: Redis
                                      ) -> Any | None:
    """Get the count of the user's daily trackers from Redis.

    :param user_id: int | str: The user's unique identifier.
    :param redis_client: Redis: The Redis client for data storage.
    :return: Any or None: The count of daily trackers or None if not found.
    """
    tracker_cnt_name: str = set_redis_name(user_id, TRACKER_CNT_PREFIX)
    return await redis_client.get(tracker_cnt_name)


async def redis_expireat_midnight(user_id: int, redis_client: Redis,
                                  day_time: None | time = None) -> Any:
    """Set a Redis key to expire at midnight.

    :param user_id: int: The user's unique identifier.
    :param redis_client: Redis: The Redis client for data storage.
    :param day_time: None | time: The time at which the key should expire (default is
     midnight).
    :return: Any: True if the key was set to expire at midnight; otherwise, False.
    """
    today = date.today()
    if not day_time:
        # Set midnight time
        when_time: time = time.max
    else:
        when_time = day_time
    today_midnight: dt = datetime.datetime.combine(today, when_time)
    tracker_cnt_name: str = set_redis_name(user_id, TRACKER_CNT_PREFIX)
    return await redis_client.expireat(name=tracker_cnt_name, when=today_midnight,
                                       nx=True)
