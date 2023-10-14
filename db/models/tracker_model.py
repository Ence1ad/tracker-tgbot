from datetime import datetime, timedelta

from sqlalchemy import Integer, ForeignKey, DateTime

from sqlalchemy.orm import mapped_column, Mapped

from db.base_model import AsyncSaBase


class TrackerModel(AsyncSaBase):
    __tablename__ = 'trackers'
    tracker_id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    duration: Mapped[timedelta] = mapped_column(nullable=True)
    track_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now
    )
    track_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.now
    )
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.category_id', ondelete='cascade'), nullable=False)
    action_id: Mapped[int] = mapped_column(ForeignKey('actions.action_id', ondelete='cascade'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='cascade'), nullable=False)
    # user = relationship("UserModel", back_populates="trackers", lazy='joined')
    # categories = relationship("CategoriesModel", back_populates="trackers", lazy='joined')
    # actions: Mapped["ActionsModel"] = relationship(backref="actions", lazy='joined')

    # __table_args__ = (
        # PrimaryKeyConstraint('tracker_id', autoincrement=True),
        # UniqueConstraint('username'),
        # ForeignKeyConstraint(columns=['user_id'], refcolumns=['user_id'], table="users",  ondelete='cascade')
        # Index(name='trackers_user_id_tracker_id_idx', expressions=['user_id', 'tracker_id']),  # composite index
    # )

    def __str__(self) -> str:
        return str(self.tracker_id)
