import datetime

from aiogram.types import CallbackQuery
from apscheduler_di import ContextSchedulerDecorator

from settings import MAX_HOURS_DURATION_TRACKER
from tgbot.schedul.schedule_funcs import schedule_delete_tracker, schedule_weekly_report


async def delete_tracker_job(
        scheduler: ContextSchedulerDecorator,
        call: CallbackQuery,
        func=schedule_delete_tracker
        ) -> None:
    scheduler.add_job(
        func=func, trigger='date',
        next_run_time=datetime.datetime.now() + datetime.timedelta(hours=MAX_HOURS_DURATION_TRACKER),
        kwargs={"user_id": call.from_user.id}
    )


async def interval_sending_reports_job(scheduler: ContextSchedulerDecorator, func=schedule_weekly_report) -> None:
    scheduler.add_job(func=func, trigger='cron', day_of_week='thu', hour=11, minute=0)
