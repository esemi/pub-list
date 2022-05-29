"""Application settings."""
import os

from pydantic import BaseSettings, RedisDsn


class AppSettings(BaseSettings):
    """Application settings class."""

    auth_cookie_key: str = 'publist_auth_cookie'
    redis_dsn: RedisDsn = 'redis://localhost:6379/1'  # type: ignore
    redis_pool_size: int = 10
    empty_tasks_on_page_max: int = 3
    empty_tasks_on_page_min: int = 1


app_settings = AppSettings(
    _env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),
)
