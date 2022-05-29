from publist import storage, schemes


async def test_unlock_task_happy_path(fixture_todolist: schemes.Todo, fixture_user: schemes.User):
    exist_task = await storage.todolist.upsert_task(fixture_todolist.uid, 'first title')
    await storage.todolist.lock_task(exist_task.uid, fixture_user.id)

    response = await storage.todolist.unlock_task(exist_task.uid)

    unlocked_task = await storage.todolist.get_task(exist_task.uid)
    assert response is True
    assert unlocked_task.bind_user is None


async def test_unlock_task_not_locked_task(fixture_todolist: schemes.Todo):
    exist_task = await storage.todolist.upsert_task(fixture_todolist.uid, 'first title')

    response = await storage.todolist.unlock_task(exist_task.uid)

    unlocked_task = await storage.todolist.get_task(exist_task.uid)
    assert response is True
    assert unlocked_task.bind_user is None


async def test_lock_task_not_found():
    response = await storage.todolist.unlock_task('invalid-task-uid')

    assert response is True
