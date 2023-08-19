from datetime import datetime
from typing import Optional

from sqlalchemy import String, PrimaryKeyConstraint, BigInteger
from sqlalchemy.orm import mapped_column, Mapped
from dataclasses import dataclass, field

from ..base_model import SqlAlchemyBase


class UserModel(SqlAlchemyBase):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(BigInteger)
    first_name: Mapped[Optional[str]] = mapped_column(String(64))
    last_name: Mapped[Optional[str]] = mapped_column(String(64))
    username: Mapped[Optional[str]] = mapped_column(String(32))
    phone: Mapped[Optional[str]] = mapped_column(String(12))
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)
    # categories: Mapped[list["CategoriesModel"]] = relationship(back_populates='user', lazy='joined')
    # trackers: Mapped[list["TrackerModel"]] = relationship(back_populates='user', lazy='joined')
    # actions: Mapped[list["ActionsModel"]] = relationship(back_populates='user', lazy='joined')

    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='user_pk'),
        # UniqueConstraint('username'),
        # ForeignKeyConstraint(['user_id'], ['users.id']),
        # Index('title_content_index' 'title', 'content'),  # composite index on title and content
    )

    def __str__(self):
        return str(self.user_id)


@dataclass
class NewUser:
    user_id: field(init=False)
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    phone: str | None = None
