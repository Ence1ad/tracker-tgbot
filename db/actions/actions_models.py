from sqlalchemy import Integer, String, Column, ForeignKey, BigInteger, UniqueConstraint

from sqlalchemy.orm import Mapped, mapped_column

from settings import LENGTH_ACTION_NAME_LIMIT
from ..base_model import SqlAlchemyBase


class ActionsModel(SqlAlchemyBase):
    __tablename__ = 'actions'
    action_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action_name: Mapped[str] = mapped_column(String(LENGTH_ACTION_NAME_LIMIT))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.category_id', ondelete='cascade'))
    user_id: Mapped[int] = Column(BigInteger, ForeignKey('users.user_id', ondelete='cascade'))
    # user = relationship("UserModel", back_populates='actions', lazy='joined')
    # categories = relationship("CategoriesModel", lazy='joined')
    # trackers = relationship("TrackerModel", back_populates='actions', lazy='joined')
    __table_args__ = (UniqueConstraint(action_name, category_id),
                      )
