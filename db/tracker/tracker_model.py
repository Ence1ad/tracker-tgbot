import datetime

from sqlalchemy import Integer, ForeignKey, DateTime

from sqlalchemy.orm import relationship, mapped_column, Mapped

from db.actions.actions_models import ActionsModel
from db.base_model import SqlAlchemyBase


class TrackerModel(SqlAlchemyBase):
    __tablename__ = 'track_time'
    tracker_id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    time_sum: Mapped[datetime.timedelta]
    creation_day: Mapped[datetime.date] = mapped_column(default=datetime.datetime.today())
    track_start: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    track_end: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.category_id', ondelete='cascade'))
    action_id: Mapped[int] = mapped_column(ForeignKey('actions.action_id', ondelete='cascade'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='cascade'))
    # user = relationship("UserModel", back_populates="trackers", lazy='joined')
    # categories = relationship("CategoriesModel", back_populates="trackers", lazy='joined')
    # actions: Mapped["ActionsModel"] = relationship(back_populates="trackers", lazy='joined')
