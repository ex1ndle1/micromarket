import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

os.environ["geo_lite_path"] = "/tmp/GeoLite2-Country.mmdb"

mock_reader_cls = MagicMock()
mock_country_response = MagicMock()
mock_country_response.country.iso_code = "US"
mock_reader_cls.return_value.country.return_value = mock_country_response

patcher = patch("geoip2.database.Reader", mock_reader_cls)
patcher.start()

from app.databases import get_db as app_get_db
from app.main import app as app_app

from user_app.databases import get_db as user_get_db
from user_app.main import app as user_app_app

patcher.stop()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def make_mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.flush = AsyncMock()
    session.close = AsyncMock()

    scalar_result = MagicMock()
    scalar_result.all.return_value = []
    session.scalars = AsyncMock(return_value=scalar_result)
    return session


@pytest_asyncio.fixture
async def app_client():
    mock_session = make_mock_session()

    def _override():
        return mock_session

    app_app.dependency_overrides[app_get_db] = _override

    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.hget.return_value = None

    with patch("app.routers.redis", mock_redis):
        transport = ASGITransport(app=app_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

    app_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_client():
    mock_session = make_mock_session()

    def _override():
        return mock_session

    user_app_app.dependency_overrides[user_get_db] = _override

    transport = ASGITransport(app=user_app_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    user_app_app.dependency_overrides.clear()
