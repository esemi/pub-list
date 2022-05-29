"""Methods for work with User entity in redis."""

from dataclasses import asdict
from typing import Optional

from publist.schemes import User
from publist.storage.redis_helpers import cleanup_uid, generate_uid, redis_pool

USER_KEY = 'publist:user:{0}'
USER_ID_INCREMENT_KEY = 'publist:user:next_user_id'


async def get_user(uid: str) -> Optional[User]:
    """Get user by UID."""
    raw_user = await redis_pool.hgetall(
        USER_KEY.format(cleanup_uid(uid)),
    )
    return User(
        id=int(raw_user.get('id')),
        auth_uid=raw_user.get('auth_uid'),
    ) if raw_user else None


async def create_user() -> User:
    """Create new user."""
    user = User(
        id=await redis_pool.incr(USER_ID_INCREMENT_KEY),
        auth_uid=generate_uid(),
    )
    await redis_pool.hset(USER_KEY.format(user.auth_uid), mapping=asdict(user))
    return user
