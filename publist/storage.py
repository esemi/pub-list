import re
import uuid
from dataclasses import asdict
from typing import Optional

import aioredis

from publist.schemes import Todo, User
from publist.settings import app_settings

UID_REGEXP = re.compile(r"[^\w]", re.IGNORECASE)

USER_KEY = 'publist:user:{}'
USER_ID_INCREMENT_KEY = 'publist:user:next_user_id'

redis_pool: aioredis.Redis = aioredis.from_url(
    app_settings.redis_dsn,
    encoding="utf-8",
    decode_responses=True,
    max_connections=app_settings.redis_pool_size,
)


async def get_user(uid: str) -> Optional[User]:
    raw_user = await redis_pool.hgetall(
        USER_KEY.format(cleanup_uid(uid))
    )
    return None if not raw_user else User(
        id=int(raw_user.get('id')),
        auth_uid=raw_user.get('auth_uid'),
    )


async def create_user() -> User:
    user = User(
        id=await redis_pool.incr(USER_ID_INCREMENT_KEY),
        auth_uid=generate_uid(),
    )
    await redis_pool.hmset(USER_KEY.format(user.auth_uid), asdict(user))
    return user


async def get_todolist(uid: str) -> Optional[Todo]:
    uid = cleanup_uid(uid)
    # todo impl
    # todo test
    return None


async def create_todolist(owner_id: int, ttl_days: int) -> Todo:
    # todo impl
    # todo test
    return Todo()


def cleanup_uid(uid: Optional[str]) -> str:
    return '' if not uid else UID_REGEXP.sub('', str(uid))


def generate_uid() -> str:
    return cleanup_uid(uuid.uuid4().hex)
