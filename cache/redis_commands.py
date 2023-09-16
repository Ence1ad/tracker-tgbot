import datetime
from datetime import datetime as dt, date, time

from redis.asyncio import Redis


async def redis_incr_user_day_trackers(user_id: int, redis_client: Redis) -> int:
    return await redis_client.incr(name=str(user_id), amount=1)


async def redis_decr_user_day_trackers(user_id: int, redis_client: Redis) -> int:
    return await redis_client.decr(name=str(user_id), amount=1)


async def redis_expireat_today_midnight(user_id: int, redis_client: Redis, day_time: None | time = None) -> int:
    today = date.today()
    if not day_time:
        midnight = time.max
    else:
        midnight = day_time
    today_midnight = datetime.datetime.combine(today, midnight)
    return await redis_client.expireat(name=str(user_id), when=today_midnight)


async def redis_sadd_user_id(user_id: int, redis_client: Redis) -> int:
    return await redis_client.sadd('users', user_id)


async def is_redis_sismember_user (user_id: int, redis_client: Redis) -> bool | None:
    user_exists = await redis_client.sismember(name="users", value=str(user_id))
    return True if user_exists else False


async def redis_smembers_users(redis_client: Redis) -> set | None:
    members = await redis_client.smembers(name="users")
    return members if members else None


async def redis_hmset_tracker_data(user_id: int, tracker_id: str, action_id: int, action_name: str, category_id: int,
                                   category_name: str, redis_client: Redis) -> None:
    call_date: dt = dt.now()
    await redis_client.hset(
        name=f"{user_id}_tracker",
        mapping={
            "start_time": str(call_date),
            "tracker_id": tracker_id,
            "action_id": action_id,
            "action_name": action_name,
            "category_id": category_id,
            "category_name": category_name
        }
    )


async def redis_hget_tracker_data(user_id: int, redis_client: Redis, key: str) -> bytes | None:
    res = await redis_client.hget(name=f"{user_id}_tracker", key=key)
    return res if res else None


async def is_redis_tracker_exist(user_id: int, redis_client: Redis) -> bool:
    tracker_exists = await redis_client.hexists(f'{user_id}_tracker', "start_time")
    return True if tracker_exists else False


async def redis_delete_tracker(user_id: int, redis_client: Redis) -> None:
    await redis_client.delete(f"{user_id}_tracker")


async def redis_hgetall_started_tracker(user_id: int, redis_client: Redis) -> dict[bytes:bytes] | None:
    return await redis_client.hgetall(f"{user_id}_tracker")


async def redis_upd_tracker(user_id: int, redis_client: Redis, tracker_id: int = None, action_id: int = None,
                            action_name: str = None, category_id: int = None, category_name: str = None) -> None:
    tracker_data = await redis_client.hgetall(f"{user_id}_tracker")
    if tracker_data:
        await redis_hmset_tracker_data(
            user_id, redis_client=redis_client, tracker_id=tracker_id or tracker_data[b'tracker_id'],
            action_id=action_id or tracker_data[b'action_id'],
            action_name=action_name or tracker_data[b'action_name'],
            category_id=category_id or tracker_data[b'category_id'],
            category_name=category_name or tracker_data[b'category_name'],
        )
