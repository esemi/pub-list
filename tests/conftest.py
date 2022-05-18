import asyncio

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.fixture()
async def app_client() -> AsyncClient:
    """
    Make a 'client' fixture available to test cases.
    """
    from publist.webapp import app

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

#
# @pytest.fixture()
# async def auth(app_client):
#     app_client.cookies.set(session_key, session)
#     yield


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
