from publist import schemes


async def test_upsert_task_api_update(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
    fixture_task: schemes.Task,
):
    response = await app_client.post(
        url=f"/{fixture_todolist.uid}/task",
        data={
            'task_uid': fixture_task.uid,
            'title': 'new title',
        },
    )

    assert response.status_code == 200
    assert response.json()['title'] == 'new title'
    assert response.json()['uid'] == fixture_task.uid


async def test_upsert_task_api_insert(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist: schemes.Todo,
):
    response = await app_client.post(
        url=f"/{fixture_todolist.uid}/task",
        data={
            'title': 'first title',
        },
    )

    assert response.status_code == 200
    assert response.json()['title'] == 'first title'
    assert response.json()['uid']


async def test_upsert_task_api_todolist_not_found(
    app_client,
    auth_by_user: schemes.User,
):
    response = await app_client.post(
        url="/invalid-todolist-uid/task",
        data={'title': 'first title'},
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'todolist not found'


async def test_upsert_task_api_by_not_author(
    app_client,
    auth_by_user: schemes.User,
    fixture_todolist_second: schemes.Todo,
):
    response = await app_client.post(
        url=f"/{fixture_todolist_second.uid}/task",
        data={'title': 'first title'},
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'todolist not authored by current user'
