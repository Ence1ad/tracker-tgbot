import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, UniqueConstraint

from sqlalchemy.orm import mapped_column, Mapped

from db.base_model import SqlAlchemyBase


class TrackerModel(SqlAlchemyBase):
    __tablename__ = 'trackers'
    tracker_id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    duration: Mapped[datetime.timedelta] = mapped_column(nullable=True)
    track_start: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    track_end: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    category_name: Mapped[int] = mapped_column(ForeignKey('categories.category_name', ondelete='cascade'), nullable=False)
    action_id: Mapped[int] = mapped_column(ForeignKey('actions.action_id', ondelete='cascade'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='cascade'), nullable=False)
    # user = relationship("UserModel", back_populates="trackers", lazy='joined')
    # categories = relationship("CategoriesModel", back_populates="trackers", lazy='joined')
    # actions: Mapped["ActionsModel"] = relationship(backref="actions", lazy='joined')

