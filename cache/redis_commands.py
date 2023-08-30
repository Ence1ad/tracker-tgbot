from datetime import datetime as dt, timedelta
from settings import redis_client
from settings import TIME_ZONE_OFFSET


# async def redis_hset_category_id(user_id: int, category_id_cb_data: int) -> None:
#     await redis_client.hset(name=user_id, key="category_id", value=category_id_cb_data)
#
#
# async def redis_hset_category_data(user_id, key, category_callback_data) -> None:
#     await redis_client.hset(name=user_id, key=key, value=category_callback_data)
#
#
# async def redis_hget_category_name(user_id: int) -> str:
#     return (await redis_client.hget(name=user_id, key='category_name')).decode(encoding='utf-8')
#
#
# async def redis_hget_category_id(user_id: int) -> int:
#     return int(await redis_client.hget(name=user_id, key="category_id"))


async def redis_hmset_tracker_data(
        user_id: int,
        call_date: dt,
        action_id: int,
        action_name: str,
        category_id: int,
        category_name: str
) -> None:
    await redis_client.hmset(name=f"{user_id}_tracker",
                             mapping={"start_time": str(call_date),
                                      "action_id": action_id,
                                      "action_name": action_name,
                                      "category_id": category_id,
                                      "category_name": category_name
                                      })


async def redis_hget_tracker_data(user_id: int, key='') -> str:
    return await redis_client.hget(name=f"{user_id}_tracker", key=key)


async def redis_is_tracker(user_id: int):
    if await redis_client.hexists(f'{user_id}_tracker', "start_time"):
        return True
    else:
        return False


async def redis_hget_start_time(user_id):
    start_time_str = (await redis_client.hget(name=f"{user_id}_tracker", key="start_time")
                      ).decode(encoding='utf-8').split('+')[0]
    launch_time = dt.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
    delta = dt.now() - (dt.strptime(start_time_str, "%Y-%m-%d %H:%M:%S"))
    return launch_time + delta


async def redis_delete_tracker(user_id):
    await redis_client.delete(f"{user_id}_tracker")


async def tracker_text(user_id: int) -> str:
    text = []
    tracker_data = await redis_client.hgetall(f"{user_id}_tracker")
    category_name: str = "🗄:" + tracker_data[b'category_name'].decode(encoding='utf-8')
    action_name: str = "🎬:" + tracker_data[b'action_name'].decode(encoding='utf-8')
    launch_time: str = tracker_data[b'start_time'].decode(encoding='utf-8').split('+')[0]
    launch_time: dt = dt.strptime(launch_time, "%Y-%m-%d %H:%M:%S")
    duration: str = "⏱:" + str((dt.now() - launch_time) - timedelta(hours=TIME_ZONE_OFFSET)).split('.')[0]
    text.extend([category_name, action_name, duration])
    text = '\n\r'.join(text)
    return text
