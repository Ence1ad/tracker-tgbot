from sqlalchemy import Integer, Date, Float
from sqlalchemy import select, extract, cast, func, and_, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config import settings
from .. import CategoriesModel
from ..actions.actions_models import ActionsModel
from ..tracker.tracker_model import TrackerModel


async def select_weekly_trackers(user_id: int, db_session: async_sessionmaker[AsyncSession]) -> list[tuple[str, int]]:
    """
    Select the records for the current week from the trackers db table by user_id

    :param user_id: Telegram user id derived from call or message
    :param db_session: AsyncSession derived from middleware
    :return: list of rows (action name, category name, day of the week, duration) from the table
    """
    async with db_session as session:
        async with session.begin():
            # Get last monday
            last_monday_subq = \
                (select(func.current_date() + cast(-6 - extract("dow", func.current_date()), Integer) % 7)
                 ).scalar_subquery()

            # Create a cte and get sorted (by tracker_id) action_id, duration, from monday to today
            # if the tracker was stopped. The limit restriction to obtain from the project settings.
            cte_stmt = \
                select(TrackerModel.action_id,
                       func.to_char(TrackerModel.track_start, 'dy').label("day_of_week"),
                       cast(func.round(
                           (func.extract('epoch', func.sum(TrackerModel.duration))/3600), 2).label("duration_action"),
                            Float)
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
                .limit(settings.USER_WEEK_TRACKERS_LIMIT)\
                .cte()

            stmt = \
                select(ActionsModel.action_name,
                       CategoriesModel.category_name,
                       text("day_of_week"),
                       func.sum(text("duration_action"))
                       )\
                .select_from(cte_stmt)\
                .join(ActionsModel)\
                .join(CategoriesModel)\
                .group_by(ActionsModel.action_name, CategoriesModel.category_name,
                          text("day_of_week")).order_by(text("day_of_week"))

            report = await session.execute(stmt)
            return report.fetchall()
