import pytest

from publist import storage

pytestmark = pytest.mark.anyio


async def test_create_todo_list_new_user(app_client):
    response = await app_client.get("/")

    assert response.headers.get('location').endswith('/edit')
    created_todolist_uid = response.text.split('/')[-1]
    assert (await storage.get_todolist(created_todolist_uid))
