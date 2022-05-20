import pytest

from publist import storage, schemes

pytestmark = pytest.mark.asyncio


async def test_get_todolist_happy_path(fixture_todolist: schemes.Todo):
    response = await storage.get_todolist(fixture_todolist.uid)

    assert isinstance(response, schemes.Todo)
    assert response.uid == fixture_todolist.uid
    assert response.owner_user_id
    assert response.tasks == []


async def test_get_todolist_not_found(fixture_todolist: schemes.Todo):
    response = await storage.get_todolist('invalid-user-uid')

    assert response is None
