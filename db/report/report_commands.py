from sqlalchemy import Integer, Sequence, Date
from sqlalchemy import select, extract, cast, func, and_

from ..actions.actions_models import Actions
from ..db_session import create_async_session
from ..tracker.tracker_model import Tracker
from sqlalchemy.dialects import postgresql
# print(select(func.now().cast(Date))))



async def get_report(user_id: int) -> Sequence:
    async with await create_async_session() as session:
        async with session.begin():
            subq = (select(
                func.current_date() + cast(-6 - extract("dow", func.current_date()), Integer) % 7)).scalar_subquery()
            report = select(Actions.action_name,
                            func.to_char(Tracker.track_start, 'dy').label("day_of_week"),
                            # cast(-1 + extract("dow", Tracker.creation_day), Integer).label("day_of_week"),
                            func.sum(Tracker.time_sum)).join(Actions) \
                .where(and_(
                Tracker.user_id == user_id,
                Tracker.track_end.is_not(None),
                Tracker.track_start.cast(Date).between(subq, func.current_date())
            )
            ).group_by(Actions.action_id, Tracker.tracker_id, Actions.action_name, Tracker.user_id,
                       cast(Tracker.track_start, Date)).order_by(Tracker.tracker_id)
            print(report)
            report = await session.execute(report)
            await session.commit()
            return report.fetchall()
