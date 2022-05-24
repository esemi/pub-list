import pytest

from publist import schemes

pytestmark = pytest.mark.asyncio


async def test_view_todo_list_page_for_customer(
    app_client,
    fixture_todolist: schemes.Todo,
):
    response = await app_client.get(f"/{fixture_todolist.uid}/view")

    assert response.status_code == 200
    assert '<html' in response.text


async def test_view_todo_list_page_for_owner(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
):
    response = await app_client.get(f"/{fixture_todolist.uid}/view")

    assert response.status_code == 200
    assert '<html' in response.text


async def test_view_todo_list_not_found(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
):
    response = await app_client.get("/invalid-todolist-uid/view")

    assert response.status_code == 307
    assert response.headers.get('location') == '/'
