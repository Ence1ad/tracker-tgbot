from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class AsyncSaBase(AsyncAttrs, DeclarativeBase):
    pass
