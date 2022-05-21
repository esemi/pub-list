"""Module for working with persistent storage."""

import re
import uuid
from dataclasses import asdict
from typing import Optional

import aioredis

from publist.schemes import Todo, User
from publist.settings import app_settings

UID_REGEXP = re.compile(r'\W', re.IGNORECASE)

USER_KEY = 'publist:user:{0}'
TODO_KEY = 'publist:todolist:{0}'
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

    # todo load tasks
    # todo sort tasks by idx

    return Todo(
        uid=raw_todolist.get('uid'),
        owner_user_id=int(raw_todolist.get('owner_user_id')),
        tasks=[],
    )


async def create_todolist(owner_id: int) -> Todo:
    """Create new todolist for specified owner-user."""
    todolist_mapping = {
        'uid': _generate_uid(),
        'owner_user_id': owner_id,
    }
    await redis_pool.hset(
        TODO_KEY.format(todolist_mapping.get('uid')),
        mapping=todolist_mapping,  # type: ignore
    )
    return Todo(
        uid=todolist_mapping['uid'],  # type: ignore
        owner_user_id=todolist_mapping['owner_user_id'],  # type: ignore
        tasks=[],
    )


def _cleanup_uid(uid: Optional[str]) -> str:
    return UID_REGEXP.sub('', str(uid)) if uid else ''


def _generate_uid() -> str:
    return _cleanup_uid(uuid.uuid4().hex)
