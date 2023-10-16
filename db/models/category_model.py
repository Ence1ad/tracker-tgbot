from sqlalchemy import String, ForeignKey, BigInteger, UniqueConstraint, \
    CheckConstraint, Identity

from sqlalchemy.orm import Mapped, mapped_column

from db.base_model import AsyncSaBase
from config import settings


class CategoryModel(AsyncSaBase):
    """Represents a category in the database.

    :cvar __tablename__: The name of the database table for categories.
    :cvar category_id: The unique identifier for the category.
    :cvar category_name: The name of the category (limited to a certain length).
    :cvar user_id: The user's ID associated with the category.
    :cvar __table_args__: Additional table arguments, including uniqueness constraints.

    - `__tablename__`: 'categories' - The name of the table.
    - `category_id`: Unique identifier for the category (primary key).
    - `category_name`: Name of the category (limited in length, not nullable).
    - `user_id`: User's ID associated with the category (foreign key, not nullable).
    - `__table_args__`: Additional table constraints.

    These constraints ensure that the category names are unique for each user and have a
     length greater than zero.
    """

    __tablename__ = 'categories'
    category_id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    category_name: Mapped[str] = mapped_column(String(settings.LENGTH_NAME_LIMIT),
                                               nullable=False)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.user_id', ondelete='cascade'), nullable=False
    )
    __table_args__ = (
        UniqueConstraint(user_id, category_name),
        CheckConstraint(sqltext="Length(category_name) > 0")
    )
