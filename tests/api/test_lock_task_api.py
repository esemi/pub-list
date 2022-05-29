from publist import schemes, storage


async def test_lock_task_api_happy_path(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
    fixture_task: schemes.Task,
):
    response = await app_client.put(
        url=f"/{fixture_todolist.uid}/task/{fixture_task.uid}",
        data={'lock_status': True},
    )

    assert response.status_code == 200
    assert response.json()['bind_user'] == auth_by_user.id


async def test_lock_task_api_unlock(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
    fixture_task: schemes.Task,
):
    await storage.todolist.lock_task(fixture_task.uid, auth_by_user.id)

    response = await app_client.put(
        url=f"/{fixture_todolist.uid}/task/{fixture_task.uid}",
        data={'lock_status': False},
    )

    assert response.status_code == 200
    assert response.json()['bind_user'] is None


async def test_lock_task_api_todolist_not_found(
    app_client,
    auth_by_user: schemes.User,
):
    response = await app_client.put(
        url="/invalid-todolist-uid/task/invalid-task-uid",
        data={'lock_status': True},
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'todolist not found'


async def test_lock_task_api_task_not_found(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
):
    response = await app_client.put(
        url=f'/{fixture_todolist.uid}/task/invalid-task-uid',
        data={'lock_status': True},
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'task not found'


async def test_lock_task_api_already_locked(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
    fixture_task: schemes.Task,
):
    await storage.todolist.lock_task(fixture_task.uid, auth_by_user.id)

    response = await app_client.put(
        url=f'/{fixture_todolist.uid}/task/{fixture_task.uid}',
        data={'lock_status': True},
    )

    assert response.status_code == 409
    assert response.json()['detail'] == 'already locked'


async def test_lock_task_api_locked_by_another_user(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
    fixture_task: schemes.Task,
    fixture_user_second: schemes.User,
):
    await storage.todolist.lock_task(fixture_task.uid, fixture_user_second.id)

    response = await app_client.put(
        url=f'/{fixture_todolist.uid}/task/{fixture_task.uid}',
        data={'lock_status': False},
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'task locked by another user'
