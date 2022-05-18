import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


@pytest.fixture()
async def app_client() -> AsyncClient:
    """
    Make a 'client' fixture available to test cases.
    """
    from publist.webapp import app

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
