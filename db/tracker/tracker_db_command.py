from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, delete, update, Sequence, func, Date, cast

from ..actions.actions_models import ActionsModel
from ..categories.categories_model import CategoriesModel
from ..db_session import create_async_session
from .tracker_model import TrackerModel


async def create_tracker(user_id: int, category_id: int, action_id: int, track_start: datetime) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            new_tracker: TrackerModel = TrackerModel(
                category_id=category_id,
                user_id=user_id,
                action_id=action_id,
                track_start=track_start
            )
            session.add(new_tracker)


async def get_user_tracker(user_id: int) -> Sequence:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = select(TrackerModel.tracker_id, TrackerModel.time_sum, ActionsModel.action_name).join(
                ActionsModel).where(
                TrackerModel.user_id == user_id,
                cast(TrackerModel.track_end, Date) == func.current_date(), TrackerModel.time_sum.is_not(None))
            res = await session.execute(stmt)
            return res.fetchall()


async def get_launch_tracker(user_id: int) -> Any | None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = select(TrackerModel.tracker_id, TrackerModel.track_start, ActionsModel.action_name,
                          CategoriesModel.category_name) \
                .join_from(TrackerModel, CategoriesModel).join_from(TrackerModel, ActionsModel) \
                .where(TrackerModel.user_id == user_id, TrackerModel.track_end.is_(None))
            res = await session.execute(stmt)
            return res.fetchall()


async def update_tracker(user_id: int, tracker_id: int, call_datetime: datetime) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = update(TrackerModel).where(TrackerModel.user_id == user_id,
                                              TrackerModel.tracker_id == tracker_id).values(
                track_end=call_datetime).execution_options(synchronize_session="fetch").returning(
                TrackerModel.track_start,
                TrackerModel.track_end)
            returning = await session.execute(stmt)
            returning = list(returning.fetchone())
            track_start = returning[0]
            track_end = returning[1]
            track_sum: timedelta = track_end - track_start
            stmt = update(TrackerModel).where(TrackerModel.user_id == user_id,
                                              TrackerModel.tracker_id == tracker_id).values(
                time_sum=track_sum).execution_options(synchronize_session="fetch")
            await session.execute(stmt)


async def delete_tracker(user_id: int, tracker_id: int):
    async with await create_async_session() as session:
        async with session.begin():
            stmt = delete(TrackerModel).where(TrackerModel.user_id == user_id,
                                              TrackerModel.tracker_id == tracker_id)
            await session.execute(stmt)
