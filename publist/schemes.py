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
    owner_user_id: int
    tasks: List[Task]
    created_at: datetime
    expired_at: datetime
