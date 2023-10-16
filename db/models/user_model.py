from datetime import datetime

from sqlalchemy import String, BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from db.base_model import AsyncSaBase


class UserModel(AsyncSaBase):
    """Represents a user in the database.

    :cvar __tablename__: The name of the database table for users.
    :cvar user_id: The unique identifier for the user (primary key).
    :cvar first_name: The user's first name (limited to 64 characters).
    :cvar last_name: The user's last name (limited to 64 characters, nullable).
    :cvar username: The user's username (limited to 32 characters, nullable).
    :cvar created_on: The timestamp when the user was created (default is the current
    timestamp).

    - `__tablename__`: 'users' - The name of the table.
    - `user_id`: Unique identifier for the user (primary key).
    - `first_name`: The user's first name (limited to 64 characters).
    - `last_name`: The user's last name (limited to 64 characters, nullable).
    - `username`: The user's username (limited to 32 characters, nullable).
    - `created_on`: The timestamp when the user was created.

    This class represents user data in the database, including their names, username,
    and creation timestamp.
    """

    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                         autoincrement=False)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str | None] = mapped_column(String(64))
    username: Mapped[str | None] = mapped_column(String(32))
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)

    def __str__(self) -> str:
        """Get a string representation of the user.

        **Returns**:

        - str: A string representation of the user, which is the user's ID.
        """
        return str(self.user_id)
