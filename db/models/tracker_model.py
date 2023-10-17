from datetime import datetime, timedelta

from sqlalchemy import ForeignKey, DateTime, Identity, Index, BigInteger

from sqlalchemy.orm import mapped_column, Mapped

from db.base_model import AsyncSaBase


class TrackerModel(AsyncSaBase):
    """Represents a tracking record in the database.

    :cvar __tablename__: The name of the database table for tracking records.
    :cvar tracker_id: The unique identifier for the tracking record (primary key).
    :cvar duration: The duration of the tracking record.
    :cvar track_start: The timestamp when tracking started (not nullable).
    :cvar track_end: The timestamp when tracking ended.
    :cvar category_id: The identifier of the associated category (not nullable).
    :cvar action_id: The identifier of the associated action (not nullable).
    :cvar user_id: The identifier of the associated user (not nullable).

    - `__tablename__`: 'trackers' - The name of the table.
    - `tracker_id`: Unique identifier for the tracking record (primary key).
    - `duration`: The duration of the tracking record.
    - `track_start`: The timestamp when tracking started (not nullable).
    - `track_end`: The timestamp when tracking ended.
    - `category_id`: The identifier of the associated category (not nullable).
    - `action_id`: The identifier of the associated action (not nullable).
    - `user_id`: The identifier of the associated user (not nullable).

    This class represents tracking records in the database, including their duration,
    start and end timestamps, category, action, and user associations.

    :func __str__: Return a string representation of the tracker's unique identifier.

    :rtype: str
    """

    __tablename__ = 'trackers'
    tracker_id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    duration: Mapped[timedelta] = mapped_column(nullable=True)
    track_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )
    track_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.now
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.category_id', ondelete='cascade'), nullable=False
    )
    action_id: Mapped[int] = mapped_column(
        ForeignKey('actions.action_id', ondelete='cascade'), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.user_id', ondelete='cascade'), nullable=False
    )

    __table_args__ = (
        Index('trackers_user_id_tracker_id_idx', 'user_id', 'tracker_id'),
    )

    def __str__(self) -> str:
        return str(self.tracker_id)
