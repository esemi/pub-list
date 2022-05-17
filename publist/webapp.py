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


def create_todo_list():
    """Create new todolist and redirect ro edit page."""
    user = _sign_in_user()

    # todo create empty todolist + ttl
    # todo redirect to edit_todo_list
    ...


def _sign_in_user() -> User:
    # todo create new user-auth or sign-in by cookie value
    ...


def edit_todo_list_page(uid: str):
    """Show edit todolist page."""
    user = _sign_in_user()
    # todo fetch todolist by uid
    ...


def show_todo_list_page(uid: str):
    """Show todolist page with bind buttons."""
    user = _sign_in_user()
    # todo fetch todolist by uid
    # todo filter empty tasks
    ...


def update_task_api(uid: str, task_idx: int, title: str) -> Task:
    """Update todolist tasks."""
    user = _sign_in_user()
    # todo check todolist ownership
    # todo update todolist.task title by idx
    ...


def lock_task_api(task_uid: str, lock_status: bool) -> Task:
    """Bind task for current logged user."""
    user = _sign_in_user()
    # todo update task.bind_user value by request
    ...


def healthz() -> str:
    return 'OK'
