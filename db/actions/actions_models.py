from sqlalchemy import Integer, String, Column, ForeignKey

from sqlalchemy.orm import relationship

from db.base_model import SqlAlchemyBase


class Actions(SqlAlchemyBase):
    __tablename__ = 'actions'
    action_id = Column(Integer, primary_key=True, autoincrement=True)
    action_name = Column(String(30), unique=True)
    category_id = Column(Integer, ForeignKey('actions_category.category_id', ondelete='cascade'))
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='cascade'))
    sa_user = relationship("SAUser", backref="actions")
    actions_categories = relationship("ActionsCategories", backref="actions")

