import datetime
from collections.abc import Callable
from typing import Any

from apscheduler.job import Job
from apscheduler_di import ContextSchedulerDecorator

from config import settings
from tgbot.schedule.schedule_funcs import schedule_delete_tracker, \
    schedule_weekly_report


async def delete_tracker_job(
        scheduler: ContextSchedulerDecorator, user_id: int, msg_text: str,
        func: Callable[[Any], None] = schedule_delete_tracker
) -> Job:
    """Schedule a job to delete a tracker after a specified duration.

    :param scheduler: ContextSchedulerDecorator: The APScheduler
    ContextSchedulerDecorator instance.
    :param user_id: int: The user's ID for whom the tracker should be deleted.
    :param msg_text: str: The message text to send to the user after deleting the
    tracker.
    :param func: (Callable[[Any], None], optional): The function to execute when the job
     runs.
            Defaults to schedule_delete_tracker.
    :return: Job: The scheduled APScheduler Job for the task.
    """
    return scheduler.add_job(
        func=func, trigger='date',
        run_date=datetime.datetime.now() + datetime.timedelta(
            hours=settings.MAX_HOURS_DURATION_TRACKER),
        kwargs={"user_id": user_id, "msg_text": msg_text}
    )


async def interval_sending_reports_job(
        scheduler: ContextSchedulerDecorator,
        func: Callable[[Any], None] = schedule_weekly_report
) -> Job:
    """Schedule a job to send reports at specified intervals.

    :param scheduler: ContextSchedulerDecorator: The APScheduler
    ContextSchedulerDecorator instance.
    :param func: (Callable[[Any], None], optional): The function to execute when the job
     runs.
            Defaults to schedule_weekly_report.
    :return: Job: The scheduled APScheduler Job for the task.
    """
    return scheduler.add_job(
        func=func, trigger='cron', day_of_week=settings.CRON_DAY_OF_WEEK,
        hour=settings.CRON_HOUR, minute=settings.CRON_MINUTE
    )
