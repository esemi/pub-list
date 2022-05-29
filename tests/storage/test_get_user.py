from publist import storage, schemes


async def test_get_user_happy_path(fixture_user: schemes.User):
    response = await storage.user.get_user(fixture_user.auth_uid)

    assert isinstance(response, schemes.User)
    assert response.id > 0
    assert response.auth_uid == fixture_user.auth_uid


async def test_get_user_not_found(fixture_user: schemes.User):
    response = await storage.user.get_user('invalid-user-uid')

    assert response is None
