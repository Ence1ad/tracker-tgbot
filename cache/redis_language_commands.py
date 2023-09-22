from redis.asyncio import Redis

from config import settings

LANG_CODE = settings.EN_LANG_CODE


async def redis_hget_lang(user_id: int,  redis_client: Redis) -> str:
    local = LANG_CODE
    local_bytes = await redis_client.hget(name='lang', key=str(user_id))
    if local_bytes:
        local = local_bytes.decode(encoding='utf-8')
    return local
