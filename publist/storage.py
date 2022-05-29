"""Module for working with persistent storage."""

import re
import uuid
from dataclasses import asdict
from typing import Optional

import aioredis

from publist.schemes import Todo, User, Task
from publist.settings import app_settings

UID_REGEXP = re.compile(r'\W', re.IGNORECASE)

USER_KEY = 'publist:user:{0}'
TODO_KEY = 'publist:todolist:{0}'
TODO_TASKS_KEY = 'publist:todolist:{0}:tasks'
TASK_KEY = 'publist:task:{0}'
USER_ID_INCREMENT_KEY = 'publist:user:next_user_id'

redis_pool: aioredis.Redis = aioredis.from_url(
    app_settings.redis_dsn,
    encoding='utf-8',
    decode_responses=True,
    max_connections=app_settings.redis_pool_size,
)


async def get_user(uid: str) -> Optional[User]:
    """Get user by UID."""
    raw_user = await redis_pool.hgetall(
        USER_KEY.format(_cleanup_uid(uid)),
    )
    return User(
        id=int(raw_user.get('id')),
        auth_uid=raw_user.get('auth_uid'),
    ) if raw_user else None


async def create_user() -> User:
    """Create new user."""
    user = User(
        id=await redis_pool.incr(USER_ID_INCREMENT_KEY),
        auth_uid=_generate_uid(),
    )
    await redis_pool.hset(USER_KEY.format(user.auth_uid), mapping=asdict(user))
    return user


async def get_todolist(uid: str) -> Optional[Todo]:
    """Get todolist by UID."""
    raw_todolist = await redis_pool.hgetall(
        TODO_KEY.format(_cleanup_uid(uid)),
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


async def create_todolist(owner_id: int) -> Todo:
    """Create new todolist for specified owner-user."""
    uid = _generate_uid()
    await redis_pool.hset(
        TODO_KEY.format(uid),
        mapping={
            'uid': uid,
            'owner_user_id': owner_id
        },
    )
    return Todo(
        uid=uid,  # type: ignore
        owner_user_id=owner_id,  # type: ignore
        tasks=[],
    )


async def get_task(uid: str) -> Optional[Task]:
    raw_task = await redis_pool.hgetall(
        TASK_KEY.format(_cleanup_uid(uid)),
    )
    if not raw_task:
        return None

    return Task(
        uid=uid,
        title=raw_task.get('title'),
        bind_user=int(raw_task.get('bind_user')) if raw_task.get('bind_user') else None,
    )


async def get_task_or_raise(uid: str) -> Task:
    task = await get_task(uid)
    if not task:
        raise RuntimeError('Task not found')
    return task


async def upsert_task(
    todolist_uid: str,
    title: str,
    task_uid: Optional[str] = None,
    bind_user: Optional[int] = None,
) -> Task:
    if not task_uid:
        task_uid = _generate_uid()

    mapping = {
        'uid': task_uid,
        'title': title,
    }

    if bind_user is not None:
        mapping['bind_user'] = str(bind_user)

    await redis_pool.hset(
        TASK_KEY.format(task_uid),
        mapping=mapping,
    )

    await redis_pool.sadd(
        TODO_TASKS_KEY.format(todolist_uid),
        task_uid,
    )

    return await get_task_or_raise(uid=task_uid)


def _cleanup_uid(uid: Optional[str]) -> str:
    return UID_REGEXP.sub('', str(uid)) if uid else ''


def _generate_uid() -> str:
    return _cleanup_uid(uuid.uuid4().hex)
