from publist import storage, schemes


async def test_remove_task_happy_path(fixture_todolist: schemes.Todo, fixture_task: schemes.Task):
    response = await storage.todolist.remove_task(fixture_todolist.uid, fixture_task.uid)

    assert response is True
    assert (await storage.todolist.get_task(fixture_task.uid)) is None
    assert (await storage.todolist.get_todolist(fixture_todolist.uid)).tasks == []


async def test_remove_task_not_found():
    response = await storage.todolist.remove_task('invalid-todolist-uid', 'invalid-task-uid')

    assert response is True

