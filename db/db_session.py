from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# You need to uncomment this func when you don't use the alembic
# async def create_tables(engine):
#     from db.base_model import AsyncSaBase
#     async with engine.begin() as conn:
#         await conn.run_sync(AsyncSaBase.metadata.create_all)


async def create_async_session(url: str, echo: bool = False) -> async_sessionmaker[AsyncSession]:
    async_engine = create_async_engine(url=url, echo=echo, query_cache_size=1200, pool_size=10,
                                       max_overflow=10)
    # expire_on_commit - don't expire objects after transaction commit
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(async_engine, expire_on_commit=False,
                                                                         class_=AsyncSession)
    # for AsyncEngine created in function scope, close and clean-up pooled connections
    await async_engine.dispose()
    return async_session
