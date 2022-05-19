import asyncio

import pytest
from httpx import AsyncClient

from publist import schemes, storage
from publist.settings import app_settings

pytestmark = pytest.mark.asyncio


@pytest.fixture()
async def app_client() -> AsyncClient:
    """
    Make a 'client' fixture available to test cases.
    """
    from publist.webapp import app

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture()
async def auth_request(app_client, fixture_user: schemes.User):
    app_client.cookies.set(app_settings.auth_cookie_key, fixture_user.auth_uid)
    yield


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def fixture_user() -> schemes.User:
    yield await storage.create_user()
