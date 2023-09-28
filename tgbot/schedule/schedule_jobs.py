import datetime
from collections.abc import Callable
from typing import Any

from apscheduler.job import Job
from apscheduler_di import ContextSchedulerDecorator

from config import settings
from tgbot.schedule.schedule_funcs import schedule_delete_tracker, schedule_weekly_report


async def delete_tracker_job(scheduler: ContextSchedulerDecorator, user_id: int, msg_text: str,
                             func: Callable[[Any], None] = schedule_delete_tracker) -> Job:
    return scheduler.add_job(
        func=func, trigger='date',
        run_date=datetime.datetime.now() + datetime.timedelta(hours=settings.MAX_HOURS_DURATION_TRACKER),
        kwargs={"user_id": user_id, "msg_text": msg_text}
    )


async def interval_sending_reports_job(scheduler: ContextSchedulerDecorator,
                                       func: Callable[[Any], None] = schedule_weekly_report) -> Job:
    return scheduler.add_job(func=func, trigger='cron', day_of_week='sun', hour=23, minute=56)
