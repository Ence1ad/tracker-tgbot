from sqlalchemy import Integer, Sequence
from sqlalchemy import select, extract, cast, func, not_

from ..actions.actions_models import Actions
from ..db_session import create_async_session
from ..tracker.tracker_model import Tracker


async def get_report(user_id: int) -> Sequence:
    async with await create_async_session() as session:
        async with session.begin():
            report = select(Actions.action_name,
                            func.to_char(Tracker.creation_day, 'dy').label("day_of_week"),
                            # cast(-1 + extract("dow", Tracker.creation_day), Integer).label("day_of_week"),
                            func.sum(Tracker.time_sum)).join(Actions) \
                .where(Tracker.user_id == user_id and not_(Tracker.track_end.is_(None)) and Tracker.track_start.between(
                 func.current_date + cast(-6 - cast(extract("dow", Tracker.track_start), Integer), Integer) % 7,
                 func.current_date)) \
                .group_by(Actions.action_id,Tracker.tracker_id, Actions.action_name, Tracker.user_id, Tracker.creation_day).order_by(
                Tracker.tracker_id)
            report = await session.execute(report)
            await session.commit()
            return report.fetchall()
