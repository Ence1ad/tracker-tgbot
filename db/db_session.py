from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

# noinspection PyUnresolvedReferences
import db.__all_models
from db.base_model import SqlAlchemyBase
from config import db_url

engine = create_async_engine(db_url, echo=False, pool_size=10, max_overflow=20)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SqlAlchemyBase.metadata.create_all)


async def create_async_session():
    await create_tables()

    # expire_on_commit - don't expire objects after transaction commit
    async_session = AsyncSession(engine, expire_on_commit=False)

    # for AsyncEngine created in function scope, close and clean-up pooled connections
    # await engine.dispose()

    return async_session
