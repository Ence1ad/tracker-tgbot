from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from cache.trackers_redis_manager import redis_hgetall_started_tracker
from datetime import datetime as dt, timedelta

from tgbot.template_engine.jinja_engine import render_template


async def _prepare_tracker_data(user_id: int, redis_client: Redis
                                ) -> dict[str, str]:
    """Prepare data for a started tracker from Redis.

    :param user_id: int: The user's unique identifier.
    :param redis_client: Redis: The Redis client for data storage.
    :return: dict[str, str]: A dictionary containing tracker data if a tracker
        is started.
    """
    tracker_data = await redis_hgetall_started_tracker(user_id=user_id,
                                                       redis_client=redis_client)

    tracker_data = \
        {key.decode(encoding='utf-8'): value.decode(encoding='utf-8')
         for key, value in tracker_data.items()}
    start_time: str = tracker_data['start_time'].split('.')[0]
    start_time_dt: dt = dt.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    tracker_data['duration'] = str((dt.now() - start_time_dt) -
                                   timedelta(seconds=0)).split('.')[0]
    return tracker_data


async def started_tracker_info(user_id: int, title: str, redis_client: Redis,
                               i18n: TranslatorRunner) -> str:
    """Generate information about a started tracker.

    :param user_id: int: The user's unique identifier.
    :param title: str: The title for the tracker.
    :param redis_client: Redis: The Redis client for data storage.
    :param i18n: TranslatorRunner: An internationalization runner for text localization.
    :return: str : Information about the started tracker in text format if a
    tracker is started.
    """
    tracker_data: dict[str, str] = await _prepare_tracker_data(user_id, redis_client)
    common_title: str = i18n.get(str(title))
    category_title: str = i18n.get('category_title')
    action_title: str = i18n.get('action_title')
    action_duration: str = i18n.get('action_duration')

    row_text: dict[str, str] = {
        'common_title': common_title,
        'category_title': category_title,
        'action_title': action_title,
        'action_duration': action_duration
    }
    text = render_template('started_tracker.html', values=tracker_data,
                           kwargs=row_text)
    return text
