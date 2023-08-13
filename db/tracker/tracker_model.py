import datetime

from sqlalchemy import Integer, Column, ForeignKey, DateTime, Interval, Date

from sqlalchemy.orm import relationship

from db.base_model import SqlAlchemyBase


class Tracker(SqlAlchemyBase):
    __tablename__ = 'track_time'
    tracker_id = Column(Integer(), primary_key=True, autoincrement=True)
    time_sum = Column(Interval())
    creation_day = Column(Date(), default=datetime.datetime.today())
    track_start = Column(DateTime(timezone=True))
    track_end = Column(DateTime(timezone=True))
    category_id = Column(Integer(), ForeignKey('actions_category.category_id', ondelete='cascade'))
    action_id = Column(Integer(), ForeignKey('actions.action_id', ondelete='cascade'))
    user_id = Column(Integer(), ForeignKey('users.user_id', ondelete='cascade'))
    sa_user = relationship("SAUser")
    actions_categories = relationship("ActionsCategories", lazy='joined')
    actions = relationship("Actions", lazy='joined')
