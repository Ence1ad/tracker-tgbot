from sqlalchemy import Integer, Sequence, Date
from sqlalchemy import select, extract, cast, func, and_, text

from ..actions.actions_models import Actions
from ..db_session import create_async_session
from ..tracker.tracker_model import Tracker


async def get_report(user_id: int) -> Sequence:
    async with await create_async_session() as session:
        async with session.begin():
            subq = (select(
                func.current_date() + cast(-6 - extract("dow", func.current_date()), Integer) % 7)).scalar_subquery()

            cte_stmt = \
                select(Tracker.action_id, func.to_char(Tracker.track_start, 'dy').label("day_of_week"),
                       # cast(-1 + extract("dow", Tracker.creation_day), Integer).label("day_of_week"),
                       func.sum(Tracker.time_sum).label("time_sum_action")) \
                .where(and_(Tracker.user_id == user_id, Tracker.track_end.is_not(None),
                            Tracker.track_start.cast(Date).between(subq, func.current_date())
                            )
                       )\
                .group_by(Tracker.action_id, Tracker.tracker_id, Tracker.user_id,
                          cast(Tracker.track_start, Date)).order_by(Tracker.tracker_id).cte()

            stmt = select(Actions.action_name, text("day_of_week"), func.sum(text("time_sum_action")))\
                .select_from(cte_stmt).join(Actions).group_by(Actions.action_name, text("day_of_week"))
            report = await session.execute(stmt)
            await session.commit()
            return report.fetchall()
