import pytest

from publist import storage, schemes

pytestmark = pytest.mark.anyio


async def test_create_user_happy_path():
    response = await storage.create_user()

    assert isinstance(response, schemes.User)
    assert response.id > 0
    assert response.auth_uid
