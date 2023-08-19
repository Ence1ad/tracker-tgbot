import datetime

from sqlalchemy import Integer, ForeignKey, DateTime

from sqlalchemy.orm import mapped_column, Mapped, relationship

from db.actions.actions_models import ActionsModel
from db.base_model import SqlAlchemyBase


class TrackerModel(SqlAlchemyBase):
    __tablename__ = 'trackers'
    tracker_id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    time_sum: Mapped[datetime.timedelta] = mapped_column(nullable=True)
    creation_day: Mapped[datetime.date] = mapped_column(default=datetime.datetime.today())
    track_start: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    track_end: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    category_name: Mapped[int] = mapped_column(ForeignKey('categories.category_name', ondelete='cascade'))
    action_name: Mapped[int] = mapped_column(ForeignKey('actions.action_name', ondelete='cascade'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='cascade'))
    # user = relationship("UserModel", back_populates="trackers", lazy='joined')
    # categories = relationship("CategoriesModel", back_populates="trackers", lazy='joined')
    actions: Mapped["ActionsModel"] = relationship(backref="actions", lazy='joined')
