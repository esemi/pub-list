import pytest

from publist import storage, schemes
from publist.settings import app_settings

pytestmark = pytest.mark.asyncio


async def test_auth_middleware_create_user(app_client):
    response = await app_client.get("/")

    auth_cookie_value = response.cookies.get(app_settings.auth_cookie_key)
    assert auth_cookie_value
    assert (await storage.get_user(auth_cookie_value)) is not None


async def test_auth_middleware_user_exist(app_client, auth_by_user: schemes.User):
    response = await app_client.get("/")

    auth_cookie_value = response.cookies.get(app_settings.auth_cookie_key)
    assert auth_cookie_value == auth_by_user.auth_uid
