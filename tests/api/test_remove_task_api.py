from publist import schemes, storage


async def test_remove_task_api_happy_path(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
    fixture_task: schemes.Task,
):
    response = await app_client.delete(
        url=f"/{fixture_todolist.uid}/task/{fixture_task.uid}",
    )

    assert response.status_code == 202
    assert (await storage.todolist.get_task(fixture_task.uid)) is None
    assert (await storage.todolist.get_todolist(fixture_todolist.uid)).tasks == []


async def test_remove_task_api_todolist_not_found(
    app_client,
    auth_by_user: schemes.User,
):
    response = await app_client.delete(
        url="/invalid-todolist-uid/task/invalid-task-uid",
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'todolist not found'


async def test_remove_task_api_task_not_found(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
):
    response = await app_client.delete(
        url=f'/{fixture_todolist.uid}/task/invalid-task-uid',
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'task not found'


async def test_remove_task_api_task_by_another_author(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist_second: schemes.Todo,
    fixture_task_second: schemes.Task,
):
    response = await app_client.delete(
        url=f'/{fixture_todolist_second.uid}/task/{fixture_task_second.uid}',
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'todolist not authored by current user'
