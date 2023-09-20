from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.redis_tracker_commands import redis_hgetall_started_tracker
from datetime import datetime as dt, timedelta

from tgbot.utils.jinja_engine import render_template


async def _prepare_tracker_data(user_id: int, redis_client: Redis) -> dict:
    tracker_data = await redis_hgetall_started_tracker(user_id=user_id, redis_client=redis_client)
    if tracker_data:
        tracker_data = \
            {key.decode(encoding='utf-8'): value.decode(encoding='utf-8') for key, value in tracker_data.items()}
        launch_time: str = tracker_data['start_time'].split('.')[0]
        launch_time: dt = dt.strptime(launch_time, "%Y-%m-%d %H:%M:%S")
        tracker_data['duration'] = str((dt.now() - launch_time) - timedelta(seconds=0)).split('.')[0]
        return tracker_data


async def started_tracker_text(user_id: int, title: str, redis_client: Redis, i18n: TranslatorRunner) -> str:
    tracker_data: dict[str: str] = await _prepare_tracker_data(user_id, redis_client)
    row_text = {
        'common_title': i18n.get(str(title)),
        'category_title': i18n.get('category_title'),
        'action_title': i18n.get('action_title'),
        'action_duration': i18n.get('action_duration')
    }
    text = render_template('started_tracker.html', values=tracker_data, kwargs=row_text)
    return text
