import datetime
from datetime import datetime as dt, time, date

from redis.asyncio import Redis


async def _tracker_name(user_id: int) -> str | None:

    """
    The _tracker_name function takes a user_id and returns the name of the tracker for that user.
        The name is in the format: &lt;user_id&gt;_tracker

    :param user_id: int: Identify the user
    :return: The name of the tracker
    """
    name = f"{user_id}_tracker"
    return name


async def redis_hmset_create_tracker(user_id: int, tracker_id: int | str, action_id: int, action_name: str,
                                     category_id: int, category_name: str, redis_client: Redis) -> int | None:

    """
    The redis_hmset_create_tracker function creates a new tracker in Redis.

    :param user_id: int: Identify the user
    :param tracker_id: int | str: Identify the tracker in redis
    :param action_id: int: Identify the action that is being tracked
    :param action_name: str: Store the name of the action in redis
    :param category_id: int: Identify the category of the action
    :param category_name: str: Store the category name in redis
    :param redis_client: Redis: Pass in the redis client object
    :return: The number of fields that were added
    """
    if user_id is not None:
        call_date: dt = dt.now()
        tracker_name: str = await _tracker_name(user_id)
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


async def redis_hget_tracker_data(user_id: int, redis_client: Redis, key: str) -> bytes | None:

    """
    The redis_hget_tracker_data function is used to retrieve a specific key from the hashmap of a user's tracker.

    :param user_id: int: Get the tracker name for a user
    :param redis_client: Redis:  Pass in the redis client object
    :param key: str: Specify the key for which we want to retrieve data from redis
    :return: The value of the key in the hash
    """
    tracker_name: str = await _tracker_name(user_id)
    res = await redis_client.hget(name=tracker_name, key=key)
    return res if res else None


async def is_redis_hexists_tracker(user_id: int | str, redis_client: Redis) -> bool:

    """
    The is_redis_hexists_tracker function checks if a user's tracker exists in Redis.

    :param user_id: int | str: Specify the user's id
    :param redis_client: Redis: Pass the redis client to the function
    :return: A boolean value
    """
    tracker_name: str = await _tracker_name(user_id)
    tracker_exists = await redis_client.hexists(tracker_name, "start_time")
    return True if tracker_exists else False


async def redis_hgetall_started_tracker(user_id: int, redis_client: Redis) -> dict[bytes:bytes] | None:

    """
    The redis_hgetall_started_tracker function is used to retrieve the started tracker for a given user.

    :param user_id: int: Specify the user_id of the user who is using this function
    :param redis_client: Redis: Pass in the redis client
    :return: A dictionary of all the
    """
    tracker_name: str = await _tracker_name(user_id)
    return await redis_client.hgetall(tracker_name)


async def redis_upd_tracker(user_id: int, redis_client: Redis, action_name: str = None,
                            category_name: str = None) -> int:

    """
    The redis_upd_tracker function updates the tracker data in Redis.

    :param user_id: int: Get the user id of a user
    :param redis_client: Redis: Pass the redis client object
    :param action_name: str: Update the action name in the tracker
    :param category_name: str: Update the category name in the tracker
    :return: 0 if the tracker data was successfully updated, 1 if not

    """
    tracker_name: str = await _tracker_name(user_id)
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


async def redis_delete_tracker(user_id: int, redis_client: Redis) -> int | None:

    """
    The redis_delete_tracker function deletes the tracker for a given user_id.


    :param user_id: int: Identify the user
    :param redis_client: Redis: Pass the redis_client object to the function
    :return: 1 if removing tracker was successfully, 0 if not
    """
    tracker_name: str = await _tracker_name(user_id)
    if await is_redis_hexists_tracker(user_id, redis_client):
        res: int = await redis_client.delete(tracker_name)
        return res


async def redis_incr_user_day_trackers(user_id: int, redis_client: Redis) -> int:

    """
    The redis_incr_user_day_trackers function increments the user's day tracker by 1.
        The function takes in a user_id and redis_client as arguments, and returns an int.

    :param user_id: int: Specify the user id of the user who is being tracked
    :param redis_client: Redis: Pass in the redis client object
    :return: The number of times the user has called it in a day
    """
    return await redis_client.incr(name=str(user_id), amount=1)


async def redis_decr_user_day_trackers(user_id: int, redis_client: Redis) -> int:

    """
    The redis_decr_user_day_trackers function is used to decrement the number of trackers a user has
        for the day. This function will be called when a user deletes one of their trackers.

    :param user_id: int: Identify the user
    :param redis_client: Redis: Pass in the redis_client object
    :return: 1 if the decrease in the number of trackers  was successfully, 0 if not

    """
    user_tracker_cnt = await redis_get_user_day_trackers(user_id, redis_client)
    if user_tracker_cnt and (int(user_tracker_cnt) > 0):
        return await redis_client.decr(name=str(user_id), amount=1)


async def redis_get_user_day_trackers(user_id: int | str, redis_client: Redis) -> bytes | None:
    """
    The redis_get_user_day_trackers function is used to retrieve the user's day trackers from Redis.

    :param user_id: int | str: Specify the user_id of the user whose trackers are being retrieved
    :param redis_client: Redis: Pass the redis client to this function
    :return: The number of user's trackers
    """
    return await redis_client.get(str(user_id))


async def redis_expireat_midnight(user_id: int, redis_client: Redis, day_time: None | time = None) -> bool:

    """
    The redis_expireat_midnight function is used to set the expiration time of a key in Redis.
        The function takes in a user_id, redis_client, and day_time as parameters.
        If no day time is provided then it will default to midnight (00:00:00).

    :param user_id: int: Identify the user in redis
    :param redis_client: Redis: Pass the redis client to the function
    :param day_time: None | time: Set the time of day when the key expires
    :return: True if the deletion was successfully, False if not

    """
    today = date.today()
    if not day_time:
        # set midnight time
        when_time = time.max
    else:
        when_time = day_time
    today_midnight = datetime.datetime.combine(today, when_time)
    return await redis_client.expireat(name=str(user_id), when=today_midnight)
