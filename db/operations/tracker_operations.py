from datetime import timedelta

from sqlalchemy import Date, desc, Sequence
from sqlalchemy import select, delete, update, func, cast
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models.action_model import ActionModel
from db.models.tracker_model import TrackerModel


async def create_tracker(user_id: int, category_id: int, action_id: int,
                         db_session: AsyncSession) -> TrackerModel:
    """Create a new tracker record in the database.

    :param user_id: The identifier of the associated user.
    :param category_id: The identifier of the associated category.
    :param action_id: The identifier of the associated action.
    :param db_session: The asynchronous database session.

    :return: The newly created TrackerModel object representing the tracker.
    """
    async with db_session as session:
        async with session.begin():
            tracker_obj: TrackerModel = \
                TrackerModel(category_id=category_id,
                             user_id=user_id,
                             action_id=action_id)
            session.add(tracker_obj)
            await session.flush()

        await session.refresh(tracker_obj)
        return tracker_obj


async def select_stopped_trackers(user_id: int, db_session: AsyncSession
                                  ) -> Sequence:
    """Select stopped trackers for a specific user from the database.

    :param user_id: The identifier of the associated user.
    :param db_session: The asynchronous database session.

    :return: A list of stopped trackers with tracker_id, duration, and action_name.
    """
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(TrackerModel.tracker_id,
                       TrackerModel.duration,
                       ActionModel.action_name)\
                .join(ActionModel) \
                .where(TrackerModel.user_id == user_id,
                       cast(TrackerModel.track_end, Date) == func.current_date(),
                       TrackerModel.duration.is_not(None))\
                .order_by(desc(TrackerModel.tracker_id))\
                .limit(settings.USER_TRACKERS_WEEKLY_LIMIT)

            res = await session.execute(stmt)
            return res.fetchall()


async def select_tracker_duration(user_id: int, tracker_id: int,
                                  db_session: AsyncSession) -> timedelta | None:
    """Select the duration of a specific tracker.

    :param user_id: The identifier of the associated user.
    :param tracker_id: The identifier of the tracker to retrieve the duration for.
    :param db_session: The asynchronous database session.

    :return: The duration of the tracker if available, None if not found.
    """
    async with db_session as session:
        async with session.begin():
            # auto_update_track_end
            udp_stmt = \
                update(TrackerModel)\
                .where(TrackerModel.user_id == user_id,
                       TrackerModel.tracker_id == tracker_id)\
                .values(duration=None)
            udp_stmt1 = \
                update(TrackerModel) \
                .where(TrackerModel.user_id == user_id,
                       TrackerModel.tracker_id == tracker_id) \
                .values(duration=TrackerModel.track_end - TrackerModel.track_start)\
                .returning(TrackerModel.duration)

            await session.execute(udp_stmt)
            duration_returning = await session.execute(udp_stmt1)
            return duration_returning.scalar_one_or_none()


async def delete_tracker(user_id: int, tracker_id: int, db_session: AsyncSession
                         ) -> int | None:
    """Delete a tracker record from the database.

    :param user_id: The identifier of the associated user.
    :param tracker_id: The identifier of the tracker to be deleted.
    :param db_session: The asynchronous database session.

    :return: The identifier of the deleted tracker if successful, None otherwise.
    """
    async with db_session as session:
        async with session.begin():
            stmt = \
                delete(TrackerModel)\
                .where(TrackerModel.user_id == user_id,
                       TrackerModel.tracker_id == tracker_id)\
                .returning(TrackerModel.tracker_id)

            returning = await session.execute(stmt)
            return returning.scalar_one_or_none()
