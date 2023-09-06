
from datetime import timedelta, datetime
from typing import Any

from sqlalchemy import Sequence, Date, Row, desc
from sqlalchemy import select, delete, update, func, cast
from sqlalchemy.ext.asyncio import AsyncSession

from ..actions.actions_models import ActionsModel
from .tracker_model import TrackerModel


async def create_tracker(user_id: int,
                         category_id: int,
                         action_id: int,
                         # track_start: datetime,
                         db_session: AsyncSession
                         ) -> TrackerModel:
    async with db_session as session:
        async with session.begin():
            tracker_obj: TrackerModel = \
                TrackerModel(category_id=category_id,
                             user_id=user_id,
                             action_id=action_id,
                             # track_start=track_start
                             )
            session.add(tracker_obj)
            await session.flush()
        await session.refresh(tracker_obj)
        return tracker_obj


async def select_stopped_trackers(user_id: int, db_session: AsyncSession) -> Sequence[Row[int, datetime, str]]:
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(TrackerModel.tracker_id,
                       TrackerModel.duration,
                       ActionsModel.action_name)\
                .join(ActionsModel) \
                .where(TrackerModel.user_id == user_id,
                       cast(TrackerModel.track_end, Date) == func.current_date(),
                       TrackerModel.duration.is_not(None)).order_by(desc(TrackerModel.tracker_id)).limit(100)
            res = await session.execute(stmt)
            return res.fetchall()


# async def select_started_tracker(user_id: int, db_session: AsyncSession) -> Any | None:
#     async with db_session as session:
#         async with session.begin():
#             stmt = \
#                 select(TrackerModel.tracker_id,
#                        TrackerModel.track_start,
#                        ActionsModel.action_name,
#                        ) \
#                 .join_from(from_=TrackerModel,
#                            target=ActionsModel,
#                            onclause=TrackerModel.action_id == ActionsModel.action_id) \
#                 .where(TrackerModel.user_id == user_id,
#                        TrackerModel.duration.is_(None))
#             res = await session.execute(stmt)
#             return res.scalar_one_or_none()


async def stop_tracker(user_id: int, tracker_id: int,
                       db_session: AsyncSession) -> timedelta | None:
    async with db_session as session:
        async with session.begin():
            udp_stmt = \
                update(TrackerModel)\
                .where(TrackerModel.user_id == user_id,
                       TrackerModel.tracker_id == tracker_id)\
                .values(duration=None)
            udp_stmt1 = \
                update(TrackerModel) \
                .where(TrackerModel.user_id == user_id,
                       TrackerModel.tracker_id == tracker_id) \
                .values(duration=TrackerModel.track_end-TrackerModel.track_start).returning(TrackerModel.duration)

            await session.execute(udp_stmt)
            duration_returning = await session.execute(udp_stmt1)
            return duration_returning.scalar_one_or_none()


async def delete_tracker(user_id: int, tracker_id: int, db_session: AsyncSession) -> int | None:
    async with db_session as session:
        async with session.begin():
            stmt = \
                delete(TrackerModel)\
                .where(TrackerModel.user_id == user_id,
                       TrackerModel.tracker_id == tracker_id).returning(TrackerModel.tracker_id)
            returning = await session.execute(stmt)
            return returning.scalar_one_or_none()
