import datetime
from datetime import datetime as dt, time, date

from redis.asyncio import Redis


async def _tracker_name(user_id: int) -> str | None:
    """
    Auxiliary function that set up tracker name for redis hashes

    :param user_id: Telegram user id derived from call or message
    :return: Tracker name based on user_id
    """
    name = f"{user_id}_tracker"
    return name


async def redis_hmset_create_tracker(user_id: int, tracker_id: int, action_id: int, action_name: str, category_id: int,
                                     category_name: str, redis_client: Redis) -> int | None:
    """
    Insert user tracker data into redis hashes

    :param user_id: Telegram user id derived from call or message
    :param tracker_id: User tracker id derived from the trackers db table
    :param action_id: User action id derived from the FSMContext state
    :param action_name: User action name derived from the FSMContext state
    :param category_id:  User category id derived from the FSMContext state
    :param category_name: User category name derived from the FSMContext state
    :param redis_client: Async Redis class derived from middleware
    :return: 6 if hmset was successful 0 if not
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
    Getting data from user tracker by key

    :param user_id: Telegram user id derived from call or message
    :param redis_client: Async Redis class derived from middleware
    :param key: The key present in the redis hashes of the user tracker
    :return: The value of the key of the redis hashes or None if the key is not found in the hashes
    """
    tracker_name: str = await _tracker_name(user_id)
    res = await redis_client.hget(name=tracker_name, key=key)
    return res if res else None


async def is_redis_hexists_tracker(user_id: int, redis_client: Redis) -> bool:
    """
    Checks the redis hash for the presence of a user tracker

    :param user_id: Telegram user id derived from call or message
    :param redis_client: Async Redis class derived from middleware
    :return: True if the user tracker exists in the redis cache, False if not
    """
    tracker_name: str = await _tracker_name(user_id)
    tracker_exists = await redis_client.hexists(tracker_name, "start_time")
    return True if tracker_exists else False


async def redis_hgetall_started_tracker(user_id: int, redis_client: Redis) -> dict[bytes:bytes] | None:
    """
    Getting all the user tracker data from the redis hashes

    :param user_id: Telegram user id derived from call or message
    :param redis_client: Async Redis class derived from middleware
    :return: User tracker data in python dict format
    """
    tracker_name: str = await _tracker_name(user_id)
    return await redis_client.hgetall(tracker_name)


async def redis_upd_tracker(user_id: int, redis_client: Redis, action_name: str = None,
                            category_name: str = None) -> int:
    """
    Updating a user tracker data in redis hashes

    :param user_id: Telegram user id derived from call or message
    :param redis_client: Async Redis class derived from middleware
    :param action_name: New action name or None
    :param category_name: New category name or None
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


async def redis_delete_tracker(user_id: int, redis_client: Redis) -> int:
    """
    Removing a user tracker from the redis db

    :param user_id: Telegram user id derived from call or message
    :param redis_client: Async Redis class derived from middleware
    :return: 1 if removing tracker was successfully, 0 if not
    """
    tracker_name: str = await _tracker_name(user_id)
    res: int = await redis_client.delete(tracker_name)
    return res


async def redis_incr_user_day_trackers(user_id: int, redis_client: Redis) -> int:
    """
    Increases by 1 when the user launches a new tracker

    :param user_id: Telegram user id derived from call or message
    :param redis_client: Async Redis class derived from middleware
    :return: 1 if the increase  was successfully, 0 if not
    """
    return await redis_client.incr(name=str(user_id), amount=1)


async def redis_decr_user_day_trackers(user_id: int, redis_client: Redis) -> int:
    """
    Decreases by 1 when the user deletes the daily tracker

    :param user_id: Telegram user id derived from call or message
    :param redis_client: Async Redis class derived from middleware
    :return: 1 if the decrease  was successfully, 0 if not
    """
    user_tracker_cnt = await redis_get_user_day_trackers(user_id, redis_client)
    if user_tracker_cnt and (int(user_tracker_cnt) > 0):
        return await redis_client.decr(name=str(user_id), amount=1)


async def redis_get_user_day_trackers(user_id: int, redis_client: Redis) -> bytes | None:
    return await redis_client.get(str(user_id))


async def redis_expireat_midnight(user_id: int, redis_client: Redis, day_time: None | time = None) -> bool:
    """
    Removes entire the user's daily tracker from the redis db when midnight arrives

    :param user_id: Telegram user id derived from call or message
    :param redis_client: Async Redis class derived from middleware
    :param day_time: Optional parameter
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
