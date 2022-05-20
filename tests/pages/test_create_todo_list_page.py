import pytest

from publist import storage, schemes

pytestmark = pytest.mark.asyncio


async def test_create_todo_list_new_user(app_client):
    response = await app_client.get("/")

    created_todolist_uid = response.headers.get('location').split('/')[1]
    created_todolist = await storage.get_todolist(created_todolist_uid)
    assert response.headers.get('location').endswith('/edit')
    assert created_todolist.tasks == []


async def test_create_todo_list_exist_user(app_client, auth_by_user: schemes.User):
    response = await app_client.get("/")

    created_todolist_uid = response.headers.get('location').split('/')[1]
    created_todolist = await storage.get_todolist(created_todolist_uid)
    assert response.headers.get('location').endswith('/edit')
    assert created_todolist.tasks == []
    assert created_todolist.owner_user_id == auth_by_user.id
