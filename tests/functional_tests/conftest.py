import pytest_asyncio

from cache.redis_tracker_commands import redis_hmset_create_tracker, redis_delete_tracker
from tests.utils import USER_ID_WITH_TRACKER_LIMIT


@pytest_asyncio.fixture(scope='class')
async def create_tracker_fixt(add_data_to_db, redis_cli):
    tracker_obj = add_data_to_db
    user_id = USER_ID_WITH_TRACKER_LIMIT
    tracker = await redis_hmset_create_tracker(
        user_id=user_id, tracker_id=tracker_obj.tracker_id, action_id=tracker_obj.action_id, action_name='',
        category_id=tracker_obj.category_id, category_name='', redis_client=redis_cli)
    yield tracker
    await redis_delete_tracker(user_id=user_id, redis_client=redis_cli)
