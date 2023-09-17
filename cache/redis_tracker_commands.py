import datetime
from datetime import datetime as dt, time, date

from redis import DataError
from redis.asyncio import Redis


async def _tracker_name(user_id: int) -> str:
    return f"{user_id}_tracker"


async def redis_hmset_tracker_data(user_id: int, tracker_id: str, action_id: int, action_name: str, category_id: int,
                                   category_name: str, redis_client: Redis) -> int:
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
    else:
        raise DataError


async def redis_hget_tracker_data(user_id: int, redis_client: Redis, key: str) -> bytes | None:
    tracker_name: str = await _tracker_name(user_id)
    res = await redis_client.hget(name=tracker_name, key=key)
    return res if res else None


async def is_redis_tracker_exist(user_id: int, redis_client: Redis) -> bool:
    tracker_name: str = await _tracker_name(user_id)
    tracker_exists = await redis_client.hexists(tracker_name, "start_time")
    return True if tracker_exists else False


async def redis_hgetall_started_tracker(user_id: int, redis_client: Redis) -> dict[bytes:bytes] | None:
    tracker_name: str = await _tracker_name(user_id)
    return await redis_client.hgetall(tracker_name)


async def redis_upd_tracker(user_id: int, redis_client: Redis, action_name: str = None, category_name: str = None) -> int:
    tracker_name: str = await _tracker_name(user_id)
    tracker_data = await redis_client.hgetall(tracker_name)
    if tracker_data:
        res = await redis_hmset_tracker_data(
            user_id, redis_client=redis_client,
            tracker_id=tracker_data[b'tracker_id'],
            action_id=tracker_data[b'action_id'],
            action_name=action_name or tracker_data[b'action_name'],
            category_id=tracker_data[b'category_id'],
            category_name=category_name or tracker_data[b'category_name'],
        )
        return res


async def redis_delete_tracker(user_id: int, redis_client: Redis) -> int:
    tracker_name: str = await _tracker_name(user_id)
    res: int = await redis_client.delete(tracker_name)
    return res


async def redis_incr_user_day_trackers(user_id: int, redis_client: Redis) -> int:
    return await redis_client.incr(name=str(user_id), amount=1)


async def redis_decr_user_day_trackers(user_id: int, redis_client: Redis) -> int:
    user_tracker_cnt = await redis_get_user_day_trackers(user_id, redis_client)
    if user_tracker_cnt and (int(user_tracker_cnt) > 0):
        return await redis_client.decr(name=str(user_id), amount=1)


async def redis_get_user_day_trackers(user_id: int, redis_client: Redis) -> bytes | None:
    return await redis_client.get(str(user_id))


async def redis_expireat_midnight(user_id: int, redis_client: Redis, day_time: None | time = None) -> int:
    today = date.today()
    if not day_time:
        # set midnight time
        when_time = time.max
    else:
        when_time = day_time
    today_midnight = datetime.datetime.combine(today, when_time)
    return await redis_client.expireat(name=str(user_id), when=today_midnight)
