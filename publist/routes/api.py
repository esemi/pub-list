"""REST-API for webapp."""

import logging
from typing import Optional, Tuple

from fastapi import APIRouter, Form, HTTPException, Path
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_409_CONFLICT

from publist import schemes, storage

router = APIRouter(tags=['api'])


@router.put('/{todolist_uid}/task/{task_uid}/lock', response_model=schemes.Task)
async def lock_task_api(
    request: Request,
    todolist_uid: str = Path(...),
    task_uid: str = Path(...),
    lock_status: bool = Form(),
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
        await _unlock_handler(task, request.state.current_user.id)  # type: ignore

    return await storage.todolist.get_task_or_raise(task_uid)


@router.post('/{todolist_uid}/task', response_model=schemes.Task)
async def upsert_task_api(
    request: Request,
    todolist_uid: str = Path(...),
    task_uid: Optional[str] = Form(None),
    title: str = Form(min_length=3),
) -> schemes.Task:
    """
    Update todolist tasks.

    Raises:
        HTTPException: For any unsuccessfully codes.
    """
    # todo test
    todolist, _ = await _parse_todolist_and_task_request(todolist_uid, task_uid)
    if todolist.owner_user_id != request.state.current_user.id:
        raise HTTPException(HTTP_403_FORBIDDEN, 'todolist not authored by current user')

    return await storage.todolist.upsert_task(todolist_uid, title, task_uid)


@router.delete('/{todolist_uid}/task/{task_uid}')
async def remove_task_api(
    request: Request,
    todolist_uid: str = Path(...),
    task_uid: str = Path(...),
):
    """
    Remove task by todolist author.

    Raises:
        HTTPException: For any unsuccessfully codes.
    """
    todolist, task = await _parse_todolist_and_task_request(todolist_uid, task_uid)
    if todolist.owner_user_id != request.state.current_user.id:
        raise HTTPException(HTTP_403_FORBIDDEN, 'todolist not authored by current user')

    await storage.todolist.remove_task(todolist.uid, task.uid)  # type: ignore
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


async def _parse_todolist_and_task_request(
    todolist_uid: str,
    task_uid: Optional[str],
) -> Tuple[schemes.Todo, Optional[schemes.Task]]:
    """
    Search todolist and (optional) included task by request.

    Raises:
        HTTPException: If Todolist or Task not found.
    """
    todolist = await storage.todolist.get_todolist(todolist_uid)
    if not todolist:
        logging.warning(f'todolist {todolist=} not found')
        raise HTTPException(HTTP_400_BAD_REQUEST, 'todolist not found')

    if task_uid is None:
        return todolist, None

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
