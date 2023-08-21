from datetime import datetime
from typing import Any

from sqlalchemy import Sequence, Date, Integer
from sqlalchemy import select, delete, update, extract, func, cast

from ..actions.actions_models import ActionsModel
from ..categories.categories_model import CategoriesModel
from ..db_session import create_async_session
from .tracker_model import TrackerModel


async def create_tracker(user_id: int, category_name: str, action_id: int, track_start: datetime) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            new_tracker: TrackerModel = \
                TrackerModel(category_name=category_name,
                             user_id=user_id,
                             action_id=action_id,
                             track_start=track_start)
            session.add(new_tracker)


async def select_trackers(user_id: int) -> Sequence:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = \
                select(TrackerModel.tracker_id,
                       TrackerModel.duration,
                       ActionsModel.action_name)\
                .join(ActionsModel) \
                .where(TrackerModel.user_id == user_id,
                       cast(TrackerModel.track_end, Date) == func.current_date(),
                       TrackerModel.duration.is_not(None))
            res = await session.execute(stmt)
            return res.fetchall()


async def select_trackers_from_monday(user_id: int) -> Sequence:
    async with await create_async_session() as session:
        async with session.begin():
            last_monday_subq = \
                (select(func.current_date() + cast(-6 - extract("dow", func.current_date()), Integer) % 7)
                 ).scalar_subquery()

            stmt = \
                select(TrackerModel.tracker_id,
                       TrackerModel.duration,
                       ActionsModel.action_name)\
                .join(ActionsModel) \
                .where(TrackerModel.user_id == user_id,
                       # TrackerModel.track_end.between(last_monday_subq, func.current_date()),
                       TrackerModel.duration.is_not(None))

            res = await session.execute(stmt)
            return res.fetchall()


async def select_started_tracker(user_id: int) -> Any | None:
    async with await create_async_session() as session:
        async with session.begin():
            stmt = \
                select(TrackerModel.tracker_id,
                       TrackerModel.track_start,
                       ActionsModel.action_name,
                       CategoriesModel.category_name) \
                .join_from(from_=TrackerModel,
                           target=ActionsModel,
                           onclause=TrackerModel.action_id == ActionsModel.action_id) \
                .join(CategoriesModel) \
                .where(TrackerModel.user_id == user_id,
                       TrackerModel.track_end.is_(None))
            res = await session.execute(stmt)
            return res.fetchall()


async def update_tracker(user_id: int, tracker_id: int, call_datetime: datetime) -> None:
    async with await create_async_session() as session:
        async with session.begin():
            udp_stmt = \
                update(TrackerModel)\
                .where(TrackerModel.user_id == user_id,
                       TrackerModel.tracker_id == tracker_id)\
                .values(track_end=call_datetime)

            udp_stmt1 = \
                update(TrackerModel) \
                .where(TrackerModel.user_id == user_id,
                       TrackerModel.tracker_id == tracker_id) \
                .values(duration=TrackerModel.track_end-TrackerModel.track_start)

            await session.execute(udp_stmt)
            await session.execute(udp_stmt1)


async def delete_tracker(user_id: int, tracker_id: int):
    async with await create_async_session() as session:
        async with session.begin():
            stmt = \
                delete(TrackerModel)\
                .where(TrackerModel.user_id == user_id,
                       TrackerModel.tracker_id == tracker_id)
            await session.execute(stmt)
