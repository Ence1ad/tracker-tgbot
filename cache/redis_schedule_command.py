from redis.asyncio import Redis


async def _set_name(name: str = "users") -> str:
    return name


async def redis_sadd_user_id(user_id: int, redis_client: Redis) -> int:
    name: str = await _set_name()
    return await redis_client.sadd(name, user_id)


async def is_redis_sismember_user(user_id: int, redis_client: Redis) -> bool | None:
    name: str = await _set_name()
    user_exists = await redis_client.sismember(name=name, value=str(user_id))
    return True if user_exists else False


async def redis_smembers_users(redis_client: Redis) -> set | None:
    name: str = await _set_name()
    members = await redis_client.smembers(name=name)
    return members if members else None
