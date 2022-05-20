"""Application settings."""
import os

from pydantic import BaseSettings, RedisDsn


class AppSettings(BaseSettings):
    """Application settings class."""

    auth_cookie_key: str = 'publist_auth_cookie'
    redis_dsn: RedisDsn = 'redis://localhost:6379/1'  # type: ignore
    redis_pool_size: int = 10


app_settings = AppSettings(
    _env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),
)
