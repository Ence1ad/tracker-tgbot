from cache.redis_cache import redis_client


async def redis_hset_category_id(user_id: int, category_id_cb_data: int) -> None:
    await redis_client.hset(name=user_id, key="category_id", value=category_id_cb_data)


async def redis_hget_category_id(user_id: int) -> int:
    return int(await redis_client.hget(name=user_id, key="category_id"))

