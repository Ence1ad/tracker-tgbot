from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class SqlAlchemyBase(AsyncAttrs, DeclarativeBase):
    pass