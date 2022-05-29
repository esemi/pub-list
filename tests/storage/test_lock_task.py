from publist import storage, schemes


async def test_lock_task_happy_path(fixture_todolist: schemes.Todo, fixture_user: schemes.User):
    exist_task = await storage.todolist.upsert_task(fixture_todolist.uid, 'first title')

    response = await storage.todolist.lock_task(exist_task.uid, fixture_user.id)

    locked_task = await storage.todolist.get_task(exist_task.uid)
    assert response is True
    assert locked_task.bind_user == fixture_user.id


async def test_lock_task_already_locked(fixture_todolist: schemes.Todo, fixture_user: schemes.User):
    exist_task = await storage.todolist.upsert_task(fixture_todolist.uid, 'first title')
    await storage.todolist.lock_task(exist_task.uid, 100500)

    response = await storage.todolist.lock_task(exist_task.uid, fixture_user.id)

    locked_task = await storage.todolist.get_task(exist_task.uid)
    assert response is False
    assert locked_task.bind_user == 100500
    assert locked_task.bind_user != fixture_user.id
