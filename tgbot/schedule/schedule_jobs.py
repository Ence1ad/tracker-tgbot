import datetime
from collections.abc import Callable
from typing import Any

from apscheduler.job import Job
from apscheduler_di import ContextSchedulerDecorator

from config import settings
from tgbot.schedule.schedule_funcs import schedule_delete_tracker, schedule_weekly_report


async def delete_tracker_job(scheduler: ContextSchedulerDecorator, user_id: int, msg_text: str,
                             func: Callable[[Any], None] = schedule_delete_tracker) -> Job:
    """
    The delete_tracker_job function is used to schedule a job that will delete the tracker
        after a certain amount of time. The default value for this function is set to 23 hours,
        but it can be changed in settings.py.

    :param scheduler: ContextSchedulerDecorator: Add a job to the scheduler
    :param user_id: int: Identify the user who sent the message
    :param msg_text: str: Delete the message that was sent to the user
    :param func: Callable[[Any]: Pass the function to be called when the job is executed
    :return: A job object
    """
    return scheduler.add_job(
        func=func, trigger='date',
        run_date=datetime.datetime.now() + datetime.timedelta(seconds=settings.MAX_HOURS_DURATION_TRACKER),
        kwargs={"user_id": user_id, "msg_text": msg_text}
    )


async def interval_sending_reports_job(scheduler: ContextSchedulerDecorator,
                                       func: Callable[[Any], None] = schedule_weekly_report) -> Job:

    return scheduler.add_job(func=func, trigger='cron', day_of_week='sun', hour=23, minute=50)
