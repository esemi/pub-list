"""Connection pool and basic helpers for redis."""

import re
import uuid
from typing import Optional

import aioredis

from publist.settings import app_settings

UID_REGEXP = re.compile(r'\W', re.IGNORECASE)

redis_pool: aioredis.Redis = aioredis.from_url(
    app_settings.redis_dsn,
    encoding='utf-8',
    decode_responses=True,
    max_connections=app_settings.redis_pool_size,
)


def cleanup_uid(uid: Optional[str]) -> str:
    """Clean potential UID string."""
    return UID_REGEXP.sub('', str(uid)) if uid else ''


def generate_uid() -> str:
    """Generate new UID."""
    return cleanup_uid(uuid.uuid4().hex)
