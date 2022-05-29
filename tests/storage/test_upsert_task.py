from publist import storage, schemes


async def test_upsert_task_insert(fixture_todolist: schemes.Todo):
    response = await storage.todolist.upsert_task(fixture_todolist.uid, 'first title', None)

    assert isinstance(response, schemes.Task)
    assert response.uid
    assert response.title == 'first title'
    assert response.bind_user is None


async def test_upsert_task_update(fixture_todolist: schemes.Todo):
    exist_task = await storage.todolist.upsert_task(fixture_todolist.uid, 'first title', None, 123)

    response = await storage.todolist.upsert_task(fixture_todolist.uid, 'updated title', task_uid=exist_task.uid)

    assert isinstance(response, schemes.Task)
    assert response.uid == exist_task.uid
    assert response.title == 'updated title'
    assert response.bind_user == 123
