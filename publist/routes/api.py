"""REST-API for webapp."""

import logging
from typing import Tuple

from fastapi import APIRouter, Form, HTTPException, Path
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_409_CONFLICT

from publist import schemes, storage

router = APIRouter(tags=['api'])


@router.put('/{todolist_uid}/task/{task_uid}/lock', response_model=schemes.Task, tags=['api'])
async def lock_task_api(
    request: Request,
    lock_status: bool = Form(...),
    todolist_uid: str = Path(...),
    task_uid: str = Path(...),
) -> schemes.Task:
    """
    Bind/unbind task for current logged user.

    Raises:
        HTTPException: For any unsuccessfully codes.
    """
    todolist, task = await _parse_todolist_and_task_request(todolist_uid, task_uid)

    if lock_status:
        await _lock_handler(task_uid, request.state.current_user.id)

    else:
        await _unlock_handler(task, request.state.current_user.id)

    return await storage.todolist.get_task(task_uid)


# @app.post('/{todolist_uid}/task/{task_uid}', response_model=Task, tags=['api'])
# async def upsert_task_api(todolist_uid: str, task_uid: Optional[int], title: str) -> Task:
#     """Update todolist tasks."""
#     # todo test
#     user = edit_sign_in_user()
#     # todo check todolist ownership
#     # todo update todolist.task title by idx
#     ...


@router.delete('/{todolist_uid}/task/{task_uid}', tags=['api'])
async def remove_task_api(request: Request, todolist_uid: str, task_uid: str):
    """
    Remove task by todolist author.

    Raises:
        HTTPException: For any unsuccessfully codes.
    """
    todolist, task = await _parse_todolist_and_task_request(todolist_uid, task_uid)
    if todolist.owner_user_id != request.state.current_user.id:
        raise HTTPException(HTTP_403_FORBIDDEN, 'todolist not authored by current user')

    await storage.todolist.remove_task(todolist.uid, task.uid)
    return JSONResponse(status_code=HTTP_202_ACCEPTED, content={})


async def _lock_handler(task_uid: str, user_id: int):
    ok = await storage.todolist.lock_task(task_uid, user_id)
    if not ok:
        logging.warning('try lock task was already locked')
        raise HTTPException(HTTP_409_CONFLICT, 'already locked')


async def _unlock_handler(task: schemes.Task, user_id: int):
    if task.bind_user != user_id:
        logging.warning('try unlock task was bind to another user')
        raise HTTPException(HTTP_400_BAD_REQUEST, 'task locked by another user')

    await storage.todolist.unlock_task(task.uid)


async def _parse_todolist_and_task_request(todolist_uid: str, task_uid: str) -> Tuple[schemes.Todo, schemes.Task]:
    """
    Search todolist and included task by request.

    Raises:
        HTTPException: If Todolist or Task not found.
    """
    todolist = await storage.todolist.get_todolist(todolist_uid)
    if not todolist:
        logging.warning(f'todolist {todolist=} not found')
        raise HTTPException(HTTP_400_BAD_REQUEST, 'todolist not found')

    try:
        task: schemes.Task = [
            task_item
            for task_item in todolist.tasks
            if task_item.uid == task_uid
        ][0]
    except IndexError:
        logging.warning(f'task {task_uid=} not found in todolist')
        raise HTTPException(HTTP_400_BAD_REQUEST, 'task not found')

    return todolist, task
