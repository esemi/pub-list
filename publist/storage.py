from typing import Optional

from publist.schemes import Todo


async def get_todolist(uid: str) -> Optional[Todo]:
    # todo impl
    # todo test
    return None


async def create_todolist(owner_id: int, ttl_days: int) -> Todo:
    # todo impl
    # todo test
    return Todo()
