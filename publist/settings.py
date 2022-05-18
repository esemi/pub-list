"""Application settings."""
import os
import re

from pydantic import BaseSettings, Field


class AppSettings(BaseSettings):
    """Application settings class."""

    todolist_ttl_days: int = Field(90, description='Как долго храним ТУДУ-лист.')
    auth_cookie_key: str = 'publist_auth_cookie'


app_settings = AppSettings(
    _env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),
)
