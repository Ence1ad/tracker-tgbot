from sqlalchemy import String, Column, ForeignKey, BigInteger, \
    UniqueConstraint, CheckConstraint, Identity

from sqlalchemy.orm import Mapped, mapped_column

from config import settings
from db.base_model import AsyncSaBase


class ActionModel(AsyncSaBase):
    """Represents an action in the database.

    :cvar __tablename__: The name of the database table for actions.
    :cvar action_id: The unique identifier for the action (primary key).
    :cvar action_name: The name of the action (limited to a length, not nullable).
    :cvar category_id: The identifier of the associated category (not nullable).
    :cvar user_id: The identifier of the associated user (not nullable).

    - `__tablename__`: 'actions' - The name of the table.
    - `action_id`: Unique identifier for the action (primary key).
    - `action_name`: The name of the action (limited to a specified length, not
     nullable).
    - `category_id`: The identifier of the associated category (not nullable).
    - `user_id`: The identifier of the associated user (not nullable).

    This class represents action data in the database, including the action's name and
     its association with a category and a user.
    """

    __tablename__ = 'actions'
    action_id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    action_name: Mapped[str] = mapped_column(
        String(settings.LENGTH_NAME_LIMIT), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.category_id', ondelete='cascade'),
        nullable=False
    )
    user_id: Mapped[int] = Column(
        BigInteger, ForeignKey('users.user_id', ondelete='cascade'), nullable=False
    )
    __table_args__ = (
        UniqueConstraint(action_name, category_id, user_id),
        CheckConstraint(sqltext="Length(action_name) > 0")
    )
