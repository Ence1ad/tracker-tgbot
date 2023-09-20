from redis.asyncio import Redis

from config import settings


async def redis_hget_lang(user_id: int,  redis_client: Redis) -> str:
    local_bytes = await redis_client.hget(name='lang', key=str(user_id))
    if local_bytes:
        local = local_bytes.decode(encoding='utf-8')
    else:
        local = settings.EN_LANG_CODE
    return local
