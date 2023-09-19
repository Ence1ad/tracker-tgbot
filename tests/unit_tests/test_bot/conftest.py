import pytest_asyncio
from aiogram.types import User

from cache.redis_tracker_commands import redis_hmset_create_tracker, redis_delete_tracker
from tests.unit_tests.test_bot.utils import USER_ID

TRACKER_ID = 1
ACTION_ID = 1
ACTION_NAME = 'action_test'
CATEGORY_ID = 1
CATEGORY_NAME = 'category_test'


@pytest_asyncio.fixture
async def create_tg_user():  # fixture factory
    async def _create_tg_user(user_id, first_name='test_name', is_bot=False):
        return User(id=user_id, first_name=first_name, is_bot=is_bot)
    return _create_tg_user


@pytest_asyncio.fixture
async def get_tracker(redis_cli):
    tracker = await redis_hmset_create_tracker(user_id=USER_ID, tracker_id=TRACKER_ID, action_id=ACTION_ID, action_name=ACTION_NAME,
                                               category_id=CATEGORY_ID, category_name=CATEGORY_NAME,
                                               redis_client=redis_cli)
    yield tracker
    await redis_delete_tracker(user_id=USER_ID, redis_client=redis_cli)