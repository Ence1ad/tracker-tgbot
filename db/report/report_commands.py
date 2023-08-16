from sqlalchemy import Integer, Sequence, Date
from sqlalchemy import select, extract, cast, func, and_, text

from ..actions.actions_models import ActionsModel
from ..db_session import create_async_session
from ..tracker.tracker_model import TrackerModel


async def get_report(user_id: int) -> Sequence:
    async with await create_async_session() as session:
        async with session.begin():
            subq = (select(
                func.current_date() + cast(-6 - extract("dow", func.current_date()), Integer) % 7)).scalar_subquery()

            cte_stmt = \
                select(TrackerModel.action_id, func.to_char(TrackerModel.track_start, 'dy').label("day_of_week"),
                       # cast(-1 + extract("dow", Tracker.creation_day), Integer).label("day_of_week"),
                       func.sum(TrackerModel.time_sum).label("time_sum_action")) \
                .where(and_(TrackerModel.user_id == user_id, TrackerModel.track_end.is_not(None),
                            TrackerModel.track_start.cast(Date).between(subq, func.current_date())
                            )
                       )\
                .group_by(TrackerModel.action_id, TrackerModel.tracker_id, TrackerModel.user_id,
                          cast(TrackerModel.track_start, Date)).order_by(TrackerModel.tracker_id).cte()

            stmt = select(ActionsModel.action_name, text("day_of_week"), func.sum(text("time_sum_action")))\
                .select_from(cte_stmt).join(ActionsModel).group_by(ActionsModel.action_name, text("day_of_week"))
            report = await session.execute(stmt)
            await session.commit()
            return report.fetchall()
