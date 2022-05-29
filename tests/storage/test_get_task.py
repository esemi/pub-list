from publist import storage, schemes


async def test_get_task_happy_path(fixture_todolist: schemes.Todo):
    exist_task = await storage.upsert_task(fixture_todolist.uid, title='test 1')

    response = await storage.get_task(exist_task.uid)

    assert isinstance(response, schemes.Task)
    assert response.uid == exist_task.uid
    assert response.bind_user is None
    assert response.title == 'test 1'


async def test_get_task_not_found(fixture_todolist: schemes.Todo):
    response = await storage.get_task('invalid-task-uid')

    assert response is None
