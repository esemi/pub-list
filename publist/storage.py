import re
import uuid
from typing import Optional

from publist.schemes import Todo, User

UID_REGEXP = re.compile(r"[^\w]", re.IGNORECASE)

USER_KEY = 'publist:user:{}'
USER_ID_INCREMENT_KEY = 'publist:user:next_user_id'


async def get_user(uid: str) -> Optional[User]:
    uid = cleanup_uid(uid)
    # todo impl
    # todo test
    return None


async def create_user() -> User:
    # todo impl
    # todo test
    user_id = await redis.incr(USER_ID_INCREMENT_KEY)
    user_uid = generate_uid('user')
    await redis.set(redis_user_auth(user_uid), user_id)
    return await get_user(user_uid)


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
    # todo test
    return '' if not uid else UID_REGEXP.sub('', str(uid))


def generate_uid(prefix: str) -> str:
    # todo test
    return cleanup_uid('{0}_{1}'.format(prefix, uuid.uuid4().hex))
