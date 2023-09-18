import datetime

from aiogram.types import CallbackQuery
from apscheduler_di import ContextSchedulerDecorator

from config import settings
from tgbot.schedule.schedule_funcs import schedule_delete_tracker, schedule_weekly_report


async def delete_tracker_job(scheduler: ContextSchedulerDecorator, call: CallbackQuery,
                             func=schedule_delete_tracker) -> None:
    scheduler.add_job(
        func=func, trigger='date',
        run_date=datetime.datetime.now() + datetime.timedelta(hours=settings.MAX_HOURS_DURATION_TRACKER),
        kwargs={"user_id": call.from_user.id}
    )


async def interval_sending_reports_job(scheduler: ContextSchedulerDecorator, func=schedule_weekly_report) -> None:
    scheduler.add_job(func=func, trigger='cron', day_of_week='sun', hour=23, minute=56)
