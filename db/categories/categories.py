from datetime import datetime

from sqlalchemy import Integer, String, Column, PrimaryKeyConstraint, DateTime, ForeignKey
from dataclasses import dataclass, field

from sqlalchemy.orm import relationship

from db.base_model import SqlAlchemyBase


class ActionsCategories(SqlAlchemyBase):
    __tablename__ = 'actions_category'
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(30), unique=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    sa_user = relationship("SAUser", backref="actions_category")