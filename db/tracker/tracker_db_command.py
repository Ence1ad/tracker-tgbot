
from datetime import timedelta, datetime
from sqlalchemy.engine.row import Row
from sqlalchemy import Date, desc
from sqlalchemy import select, delete, update, func, cast
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config import settings
from ..actions.actions_models import ActionsModel
from .tracker_model import TrackerModel


async def create_tracker(user_id: int, category_id: int, action_id: int,
                         db_session: async_sessionmaker[AsyncSession]) -> TrackerModel:
    """
    Create a record in the trackers db table and return the obj

    :param user_id: Telegram user id derived from call or message
    :param category_id: Category id derived from the cache
    :param action_id: Action id derived from the cache
    :param db_session: AsyncSession derived from middleware
    :return: TrackerModel.tracker_id object
    """
    async with db_session as session:
        async with session.begin():
            tracker_obj: TrackerModel = \
                TrackerModel(category_id=category_id, user_id=user_id, action_id=action_id)
            session.add(tracker_obj)
            await session.flush()

        await session.refresh(tracker_obj)
        return tracker_obj


async def select_stopped_trackers(user_id: int, db_session: async_sessionmaker[AsyncSession]
                                  ) -> list[Row[int, datetime, str]]:
    """
    The select_stopped_trackers function is used to select the last USER_TRACKERS_WEEKLY_LIMIT trackers that have been
    stopped by a user. The function takes in two arguments:

    :param user_id: int: Identify the user
    :param db_session: async_sessionmaker[AsyncSession]: Pass the database session to the function
    :return: A list of rows(tuples)
    """
    async with db_session as session:
        async with session.begin():
            stmt = \
                select(TrackerModel.tracker_id,
                       TrackerModel.duration,
                       ActionsModel.action_name)\
                .join(ActionsModel) \
                .where(TrackerModel.user_id == user_id,
                       cast(TrackerModel.track_end, Date) == func.current_date(),
                       TrackerModel.duration.is_not(None))\
                .order_by(desc(TrackerModel.tracker_id))\
                .limit(settings.USER_TRACKERS_WEEKLY_LIMIT)

            res = await session.execute(stmt)
            return res.fetchall()


async def select_tracker_duration(user_id: int, tracker_id: int,
                                  db_session: async_sessionmaker[AsyncSession]) -> timedelta | None:

    """
    The select_tracker_duration function is used to select the duration of a tracker.

    :param user_id: int: Identify the user
    :param tracker_id: int: Identify the tracker that is being updated
    :param db_session: async_sessionmaker[AsyncSession]: Pass the database session to the function
    :return: Duration (a timedelta object) if the update operation was successful, none if not
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


async def delete_tracker(user_id: int, tracker_id: int, db_session: async_sessionmaker[AsyncSession]) -> int | None:

    """
    The delete_tracker function deletes a tracker from the database.

    :param user_id: int: Specify the user_id of the tracker to be deleted
    :param tracker_id: int: Specify which tracker to delete
    :param db_session: async_sessionmaker[AsyncSession]: Pass the database session to the function
    :return: one if the deleted row or none if no rows were deleted
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
