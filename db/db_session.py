from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


async def create_async_session(url: str, echo: bool = False) -> async_sessionmaker[AsyncSession]:
    """
    Creates an async_sessionmaker object that can be used to create async sessions.

    The function takes thr url argument, which is the database connection string, and an echo
    argument (default False), which determines whether SQLAlchemy will log all queries to stdout. The
    create_async_session function returns the async session maker object.

    :param url: str: Specify the database connection string
    :param echo: bool: Turn on sqlalchemy logging
    :return: An async_sessionmaker object
    """
    async_engine = create_async_engine(url=url, echo=echo, query_cache_size=1200, pool_size=10,
                                       max_overflow=10)
    # expire_on_commit - don't expire objects after transaction commit
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(async_engine, expire_on_commit=False,
                                                                         class_=AsyncSession)
    # for AsyncEngine created in function scope, close and clean-up pooled connections
    await async_engine.dispose()
    return async_session
