from aiogram.fsm.storage import redis
from redis.asyncio.client import Redis

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_client = Redis(connection_pool=pool)

