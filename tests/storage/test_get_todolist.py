from publist import storage, schemes


async def test_get_todolist_happy_path(fixture_todolist: schemes.Todo):
    response = await storage.todolist.get_todolist(fixture_todolist.uid)

    assert isinstance(response, schemes.Todo)
    assert response.uid == fixture_todolist.uid
    assert response.owner_user_id
    assert response.tasks == []


async def test_get_todolist_with_tasks(fixture_todolist: schemes.Todo):
    await storage.todolist.upsert_task(fixture_todolist.uid, title='test 1')
    await storage.todolist.upsert_task(fixture_todolist.uid, title='test 2')

    response = await storage.todolist.get_todolist(fixture_todolist.uid)

    assert len(response.tasks) == 2


async def test_get_todolist_not_found(fixture_todolist: schemes.Todo):
    response = await storage.todolist.get_todolist('invalid-user-uid')

    assert response is None
