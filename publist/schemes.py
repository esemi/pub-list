"""App-specific types."""

from dataclasses import dataclass
from typing import List


@dataclass
class User:
    """Owner or customer user."""

    id: int
    auth_uid: str


@dataclass
class Task:
    """Task from todolist."""

    idx: int
    uid: str
    bind_user: int
    title: str


@dataclass
class Todo:
    """Set of tasks."""

    uid: str
    owner_user_id: int
    tasks: List[Task]
