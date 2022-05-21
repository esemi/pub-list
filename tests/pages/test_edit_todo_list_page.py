import pytest

from publist import schemes

pytestmark = pytest.mark.asyncio


async def test_edit_todo_list_happy_path(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
):
    response = await app_client.get(f"/{fixture_todolist.uid}/edit")

    assert response.status_code == 200
    assert '<html' in response.text


async def test_edit_todo_list_not_found(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
):
    response = await app_client.get("/invalid-todolist-uid/edit")

    assert response.status_code == 307
    assert response.headers.get('location') == '/'


async def test_edit_todo_list_access_denied(
    app_client,
    fixture_todolist: schemes.Todo,
):
    response = await app_client.get(f"/{fixture_todolist.uid}/edit")

    assert response.status_code == 307
    assert response.headers.get('location').endswith('view')
