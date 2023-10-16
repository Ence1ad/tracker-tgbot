from sqlalchemy import Integer, Date, Float, Sequence
from sqlalchemy import select, extract, cast, func, and_, text
from sqlalchemy.ext.asyncio import AsyncSession


from config import settings
from db import CategoryModel
from db.models.action_model import ActionModel
from db.models.tracker_model import TrackerModel


async def select_weekly_trackers(user_id: int, db_session: AsyncSession
                                 ) -> Sequence:
    """Select weekly tracker data for a specific user from the database.

    This function retrieves and aggregates data related to trackers for a specific user
    over the past week, providing a summary of tracked actions and their durations for
    each day of the week.

    :param user_id: The identifier of the associated user.
    :param db_session: The asynchronous database session.

    :return: A list of rows containing action and category names, day of the week, and
    total duration for each action-category pair. The list is sorted by the day of
    the week.
    """
    async with db_session as session:
        async with session.begin():
            # Get last monday
            last_monday_subq = \
                select(func.current_date() +
                       cast(-6 - extract("dow", func.current_date()), Integer) % 7)\
                .scalar_subquery()
            # Create a cte and get sorted (by tracker_id) action_id, duration, from
            # monday to today if the tracker was stopped. The limit restriction to
            # obtain from the project settings.
            cte_stmt = \
                select(
                    TrackerModel.action_id,
                    func.to_char(TrackerModel.track_start, 'dy')
                    .label("day_of_week"),
                    cast(func.round(
                        (func.extract('epoch', func.sum(TrackerModel.duration))/3600),
                        2).label("duration_action"), Float)
                ) \
                .where(and_(TrackerModel.user_id == user_id,
                            TrackerModel.track_end.is_not(None),
                            TrackerModel.track_start.cast(Date)
                            .between(last_monday_subq, func.current_date())
                            )
                       )\
                .group_by(TrackerModel.action_id,
                          TrackerModel.tracker_id,
                          TrackerModel.user_id,
                          cast(TrackerModel.track_start, Date)
                          )\
                .order_by(TrackerModel.tracker_id)\
                .limit(settings.USER_TRACKERS_WEEKLY_LIMIT)\
                .cte()

            stmt = \
                select(ActionModel.action_name,
                       CategoryModel.category_name,
                       text("day_of_week"),
                       func.sum(text("duration_action"))
                       )\
                .select_from(cte_stmt)\
                .join(ActionModel)\
                .join(CategoryModel)\
                .group_by(ActionModel.action_name, CategoryModel.category_name,
                          text("day_of_week")).order_by(text("day_of_week"))

            report = await session.execute(stmt)
            return report.fetchall()
