from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


# Use when you don't use alembic
# async def create_tables(engine):
#     from db.base_model import SqlAlchemyBase
#     async with engine.begin() as conn:
#         await conn.run_sync(SqlAlchemyBase.metadata.create_all)


async def create_async_session(engine):
    # await create_tables(engine)
    # expire_on_commit - don't expire objects after transaction commit
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
    # for AsyncEngine created in function scope, close and clean-up pooled connections
    await engine.dispose()
    return async_session
