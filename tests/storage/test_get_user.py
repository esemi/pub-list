import pytest

from publist import storage, schemes

pytestmark = pytest.mark.asyncio


async def test_get_user_happy_path():
    user = await storage.create_user()

    response = await storage.get_user(user.auth_uid)

    assert isinstance(response, schemes.User)
    assert response.id > 0
    assert response.auth_uid == user.auth_uid


async def test_get_user_not_found():
    response = await storage.get_user('invalid-user-uid')

    assert response is None
