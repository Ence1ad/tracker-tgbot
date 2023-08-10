from datetime import datetime

from sqlalchemy import Integer, String, Column, PrimaryKeyConstraint, DateTime
from dataclasses import dataclass, field
from ..base_model import SqlAlchemyBase


class SAUser(SqlAlchemyBase):
    __tablename__ = 'users'
    user_id = Column(Integer)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    username = Column(String(100), nullable=True)
    phone = Column(String(100), nullable=True)
    created_on = Column(DateTime(), default=datetime.now)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='user_pk'),
        # UniqueConstraint('username'),
        # ForeignKeyConstraint(['user_id'], ['users.id']),
        # Index('title_content_index' 'title', 'content'),  # composite index on title and content
    )


# TODO можно заморочиться и переписать на SQLModel когда библиотека начнет поддерживать async запросы
@dataclass
class NewUser:
    user_id: field(init=False)
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    phone: str | None = None
