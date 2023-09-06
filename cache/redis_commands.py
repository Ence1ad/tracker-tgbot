from datetime import datetime as dt, timedelta
from settings import redis_client


async def redis_add_user_id(user_id: int) -> int:
    return await redis_client.sadd('users', user_id)


async def is_redis_have_user(user_id) -> bool | None:
    user_exists = await redis_client.sismember(name="users", value=user_id)
    return True if user_exists else False


async def redis_get_members() -> set | None:
    members = await redis_client.smembers(name="users")
    return members if members else None


async def redis_hmset_tracker_data(
        user_id: int,
        tracker_id: str,
        action_id: int,
        action_name: str,
        category_id: int,
        category_name: str
) -> None:
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


async def redis_hget_tracker_data(user_id: int, key='') -> bytes | None:
    res = await redis_client.hget(name=f"{user_id}_tracker", key=key)
    return res if res else None


async def is_redis_tracker_exist(user_id: int):
    tracker_exists = await redis_client.hexists(f'{user_id}_tracker', "start_time")
    return True if tracker_exists else False


async def redis_delete_tracker(user_id):
    await redis_client.delete(f"{user_id}_tracker")


async def redis_started_tracker(user_id: int) -> str:
    text = []
    tracker_data = await redis_client.hgetall(f"{user_id}_tracker")
    if tracker_data:
        category_name: str = "🗄:" + ' ' + tracker_data[b'category_name'].decode(encoding='utf-8')
        action_name: str = "🎬:" + ' ' + tracker_data[b'action_name'].decode(encoding='utf-8')
        launch_time: str = tracker_data[b'start_time'].decode(encoding='utf-8').split('.')[0]
        launch_time: dt = dt.strptime(launch_time, "%Y-%m-%d %H:%M:%S")
        duration: str = "⏱:" + ' ' + str((dt.now() - launch_time) - timedelta(seconds=0)).split('.')[0]
        text.extend([category_name, action_name, duration])
        text = '\n\r'.join(text)
        return text


async def redis_upd_tracker(
        user_id: int,
        tracker_id=None,
        action_id=None,
        action_name=None,
        category_id=None,
        category_name=None
) -> None:
    tracker_data = await redis_client.hgetall(f"{user_id}_tracker")
    if tracker_data:
        await redis_hmset_tracker_data(
            user_id,
            tracker_id=tracker_id or tracker_data[b'tracker_id'],
            action_id=action_id or tracker_data[b'action_id'],
            action_name=action_name or tracker_data[b'action_name'],
            category_id=category_id or tracker_data[b'category_id'],
            category_name=category_name or tracker_data[b'category_name']
        )
