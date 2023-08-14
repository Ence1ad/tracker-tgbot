from datetime import datetime, timedelta

from sqlalchemy import select, delete, update, Sequence, func, Date

from ..actions.actions_models import Actions
from ..db_session import create_async_session
from .tracker_model import Tracker


async def create_tracker(user_id: int, category_id: int, action_id: int, track_start: datetime) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            new_tracker: Tracker = Tracker(
                category_id=category_id,
                user_id=user_id,
                action_id=action_id,
                track_start=track_start
            )
            session.add(new_tracker)
            await session.commit()


async def get_user_tracker(user_id: int) -> Sequence:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = select(Tracker.tracker_id, Tracker.time_sum, Actions.action_name).join(Actions).where(Tracker.user_id == user_id,
                          Tracker.track_end.cast(Date) == func.current_date(), Tracker.time_sum.is_not(None))
            print(stmt)
            res = await session.execute(stmt)
            await session.commit()
            return res.fetchall()


async def get_launch_tracker(user_id: int) -> Tracker:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = select(Tracker).where(Tracker.user_id == user_id, Tracker.track_end.is_(None))
            res = await session.execute(stmt)
            await session.commit()
            return res.first()


async def update_tracker(user_id: int, tracker_id: int, call_datetime: datetime) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = update(Tracker).where(Tracker.user_id == user_id, Tracker.tracker_id == tracker_id).values(
                track_end=call_datetime).execution_options(synchronize_session="fetch").returning(Tracker.track_start, Tracker.track_end)
            returning = await session.execute(stmt)
            returning = list(returning.fetchone())
            track_start = returning[0]
            track_end = returning[1]
            track_sum: timedelta = track_end - track_start
            stmt = update(Tracker).where(Tracker.user_id == user_id, Tracker.tracker_id == tracker_id).values(
                time_sum=track_sum).execution_options(synchronize_session="fetch")
            await session.execute(stmt)
            await session.commit()


async def delete_tracker(user_id: int, tracker_id: int):
    async with await create_async_session() as session:
        async with session.begin():
            stmt = delete(Tracker).where(Tracker.user_id == user_id,
                                         Tracker.tracker_id == tracker_id)
            await session.execute(stmt)
            await session.commit()
