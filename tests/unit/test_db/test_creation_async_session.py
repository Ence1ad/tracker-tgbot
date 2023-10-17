import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.db_session import create_async_session


@pytest.mark.asyncio
class TestCreateAsyncSession:

    async def test_create_async_session(self, _database_url):
        db_session = await create_async_session(url=_database_url)
        assert isinstance(db_session, async_sessionmaker)
