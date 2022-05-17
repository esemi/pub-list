from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class User:
    id: int
    auth_uid: str


@dataclass
class Task:
    idx: int
    uid: str
    bind_user: int
    title: str


@dataclass
class Todo:
    owner_user: int
    tasks: List[Task]
    created_at: datetime
    expired_at: datetime


def sign_up() -> User:
    # todo create new user-auth or sign-in by cookie value
    ...


def create_todo_list(required_auth_user: User) -> Todo:
    """Create new todolist."""
    # todo create empty todolist
    ...


def get_todo_list(uid: str, required_auth_user: User) -> Todo:
    """Fetch complete todolist with all tasks."""
    # todo fetch todolist by uid
    ...


def update_todo_list_task(uid: str, task_idx: int, title: str, required_auth_user: User) -> Task:
    """Update todolist tasks."""
    # todo check todolist ownership
    # todo update todolist.task title by idx
    ...


def bind_todo_list_task(task_uid: str, required_auth_user: User) -> Task:
    """Bind task for current logged user."""
    # todo update task.bind_user value by request
    ...
