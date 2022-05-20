import pytest

from publist import storage, schemes

pytestmark = pytest.mark.asyncio


async def test_create_user_happy_path(fixture_user: schemes.User):
    response = await storage.create_todolist(fixture_user.id)

    assert isinstance(response, schemes.Todo)
    assert response.uid
    assert response.owner_user_id == fixture_user.id
    assert response.tasks == []