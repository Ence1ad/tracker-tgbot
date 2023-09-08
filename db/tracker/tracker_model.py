from datetime import datetime, timedelta

from sqlalchemy import Integer, ForeignKey, DateTime

from sqlalchemy.orm import mapped_column, Mapped

from db.base_model import SqlAlchemyBase


class TrackerModel(SqlAlchemyBase):
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

    def __str__(self) -> str:
        return str(self.tracker_id)
