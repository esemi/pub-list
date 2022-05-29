"""App-specific types."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class User:
    """Owner or customer user."""

    id: int
    auth_uid: str


@dataclass
class Task:
    """Task from todolist."""

    uid: str
    title: str
    bind_user: Optional[int]


@dataclass
class Todo:
    """Set of tasks."""

    uid: str
    owner_user_id: int
    tasks: List[Task]
