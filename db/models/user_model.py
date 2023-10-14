from datetime import datetime
from typing import Optional

from sqlalchemy import String, BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from db.base_model import AsyncSaBase


class UserModel(AsyncSaBase):
    """
    SQLAlchemy model representing user data.

    This class defines an SQLAlchemy model for storing user data in a database. It includes fields
    such as user ID, first name, last name, username, and the date and time the user was created.

    **Attributes**:

    - ``user_id`` (Mapped[int]): The primary key representing the user's ID.
    - ``first_name`` (Mapped[str]): The user's first name.
    - ``last_name`` (Mapped[Optional[str]]): The user's last name (optional).
    - ``username`` (Mapped[Optional[str]]): The user's username (optional).
    - ``created_on`` (Mapped[datetime]): The date and time the user was created
    (with a default value of the current time).

    **Methods**:

    - ``__str__()``: Returns a string representation of the user, which is the user's ID.

    **Table Name**:

    - ``__tablename__`` (str): The name of the database table where user data is stored
    (set to 'users').

    This class inherits from AsyncSaBase, which is a base class for asynchronous SQLAlchemy models.
    """

    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[Optional[str]] = mapped_column(String(64))
    username: Mapped[Optional[str]] = mapped_column(String(32))
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)

    def __str__(self) -> str:
        """
        Get a string representation of the user.

        **Returns**:

        - str: A string representation of the user, which is the user's ID.
        """
        return str(self.user_id)
