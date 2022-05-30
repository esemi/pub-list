"""Methods for work with Todolist and Task entities in redis."""
from typing import Optional

from publist.schemes import Task, Todo
from publist.storage.redis_helpers import cleanup_uid, generate_uid, redis_pool

TODO_KEY = 'publist:todolist:{0}'
TODO_TASKS_KEY = 'publist:todolist:{0}:tasks'
TASK_KEY = 'publist:task:{0}'
TASK_BINDING_LOCK_KEY = 'publist:task:{0}:lock'


async def get_todolist(uid: str) -> Optional[Todo]:
    """Get todolist by UID."""
    raw_todolist = await redis_pool.hgetall(
        TODO_KEY.format(cleanup_uid(uid)),
    )
    if not raw_todolist:
        return None

    tasks = [
        await get_task_or_raise(task_uid)
        for task_uid in await redis_pool.smembers(TODO_TASKS_KEY.format(uid))
    ]

    return Todo(
        uid=raw_todolist.get('uid'),
        owner_user_id=int(raw_todolist.get('owner_user_id')),
        tasks=tasks,
    )


async def get_task(uid: str) -> Optional[Task]:
    """Search task by uid."""
    raw_task = await redis_pool.hgetall(
        TASK_KEY.format(cleanup_uid(uid)),
    )
    if not raw_task:
        return None

    return Task(
        uid=uid,
        title=raw_task.get('title'),
        bind_user=int(raw_task.get('bind_user')) if raw_task.get('bind_user') else None,
    )


async def get_task_or_raise(uid: str) -> Task:
    """
    Search task by uid and raise exception in nothing found case.

    Raises:
        RuntimeError: Task not found by uid.
    """
    task = await get_task(uid)
    if not task:
        raise RuntimeError('Task not found')
    return task


async def create_todolist(owner_id: int) -> Todo:
    """Create new todolist for specified owner-user."""
    uid = generate_uid()
    await redis_pool.hset(
        TODO_KEY.format(uid),
        mapping={
            'uid': uid,
            'owner_user_id': owner_id,
        },
    )
    return Todo(
        uid=uid,  # type: ignore
        owner_user_id=owner_id,  # type: ignore
        tasks=[],
    )


async def upsert_task(
    todolist_uid: str,
    title: str,
    task_uid: Optional[str] = None,
) -> Task:
    """Insert or update task."""
    if not task_uid:
        task_uid = generate_uid()

    todolist_uid = cleanup_uid(todolist_uid)
    task_uid = cleanup_uid(task_uid)

    mapping = {
        'uid': task_uid,
        'title': title,
    }

    await redis_pool.hset(
        TASK_KEY.format(task_uid),
        mapping=mapping,
    )

    await redis_pool.sadd(
        TODO_TASKS_KEY.format(todolist_uid),
        task_uid,
    )

    return await get_task_or_raise(uid=task_uid)


async def lock_task(
    task_uid: str,
    user_id: int,
) -> bool:
    """Lock task for user."""
    task_uid = cleanup_uid(task_uid)
    lock_task_result = await redis_pool.incr(TASK_BINDING_LOCK_KEY.format(task_uid))
    if lock_task_result > 1:
        return False

    await redis_pool.hset(
        TASK_KEY.format(task_uid),
        key='bind_user',
        value=user_id,
    )
    return True


async def unlock_task(
    task_uid: str,
) -> bool:
    """Unlock task from user."""
    task_uid = cleanup_uid(task_uid)

    await redis_pool.hdel(
        TASK_KEY.format(task_uid),
        'bind_user',
    )
    await redis_pool.delete(TASK_BINDING_LOCK_KEY.format(task_uid))
    return True


async def remove_task(
    todolist_uid: str,
    task_uid: str,
) -> bool:
    """Remove task."""
    # todo test
    todolist_uid = cleanup_uid(todolist_uid)
    task_uid = cleanup_uid(task_uid)

    await redis_pool.delete(TASK_KEY.format(task_uid))

    await redis_pool.srem(
        TODO_TASKS_KEY.format(todolist_uid),
        task_uid,
    )
    return True
