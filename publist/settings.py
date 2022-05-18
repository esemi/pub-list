"""Application settings."""
import os

from pydantic import BaseSettings, Field, RedisDsn


class AppSettings(BaseSettings):
    """Application settings class."""

    todolist_ttl_days: int = Field(90, description='Как долго храним ТУДУ-лист.')
    auth_cookie_key: str = 'publist_auth_cookie'
    redis_dsn: RedisDsn = 'redis://localhost:6379/1'
    redis_pool_size: int = 10


app_settings = AppSettings(
    _env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),
)
