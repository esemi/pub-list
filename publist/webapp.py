"""Todolist web app."""
import logging
import pathlib
from http import HTTPStatus
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Path, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT

from publist import storage
from publist.schemes import Task, User
from publist.settings import app_settings

logging.basicConfig(level=logging.INFO)
app_path = pathlib.Path(__file__).resolve().parent

app = FastAPI()
app.mount('/static', StaticFiles(directory=app_path.joinpath('static')), name='static')
templates = Jinja2Templates(directory=app_path.joinpath('templates'))


@app.middleware('http')
async def sign_in_user_middleware(request: Request, call_next) -> Response:
    """Auth user by cookie value."""
    auth_cookie_value = request.cookies.get(app_settings.auth_cookie_key)

    auth_user: Optional[User] = None
    if auth_cookie_value:
        auth_user = await storage.user.get_user(uid=auth_cookie_value)
    if not auth_user:
        auth_user = await storage.user.create_user()

    request.state.current_user = auth_user
    response: Response = await call_next(request)
    response.set_cookie(app_settings.auth_cookie_key, auth_user.auth_uid)

    return response


@app.get('/', response_class=RedirectResponse, status_code=HTTPStatus.TEMPORARY_REDIRECT, tags=['pages'])
async def create_todo_list_page(request: Request):
    """Create new todolist and redirect ro edit page."""
    created_todolist = await storage.todolist.create_todolist(request.state.current_user.id)
    logging.info(f'create new todolist {created_todolist.uid=}')
    return app.url_path_for('edit_todo_list_page', uid=created_todolist.uid)


@app.get('/{uid}/edit', response_class=HTMLResponse, tags=['pages'])
async def edit_todo_list_page(uid: str, request: Request):
    """Show edit todolist page."""
    todolist = await storage.todolist.get_todolist(uid)
    if not todolist:
        logging.warning(f'todolist {uid=} not found')
        return RedirectResponse(app.url_path_for('create_todo_list_page'))

    if todolist.owner_user_id != request.state.current_user.id:
        logging.warning('todolist {0} - owner mistake ({1} given)'.format(
            uid,
            request.state.current_user.id,
        ))
        return RedirectResponse(app.url_path_for('view_todo_list_page', uid=uid))

    return templates.TemplateResponse('edit.html', {
        'request': request,
        'todolist': todolist,
        'empty_task_count': max(
            app_settings.empty_tasks_on_page_min,
            app_settings.empty_tasks_on_page_max - len(todolist.tasks),
        ),
    })


@app.get('/{uid}/view', response_class=HTMLResponse, tags=['pages'])
async def view_todo_list_page(uid: str, request: Request):
    """Show todolist page with bind buttons."""
    todolist = await storage.todolist.get_todolist(uid)
    if not todolist:
        logging.warning(f'todolist {uid=} not found')
        return RedirectResponse(app.url_path_for('create_todo_list_page'))

    todolist.tasks = [task for task in todolist.tasks if task.title]

    return templates.TemplateResponse('view.html', {
        'request': request,
        'todolist': todolist,
        'current_user_id': request.state.current_user.id,
    })


# async def remove_task_api(todolist_uid: str, task_uid: Optional[int], title: str) -> Task:

# async def upsert_task_api(todolist_uid: str, task_uid: Optional[int], title: str) -> Task:
#     """Update todolist tasks."""
#     # todo test
#     user = edit_sign_in_user()
#     # todo check todolist ownership
#     # todo update todolist.task title by idx
#     ...

@app.put('/{todolist_uid}/task/{task_uid}', response_model=Task, tags=['api'])
async def lock_task_api(
    request: Request,
    lock_status: bool = Form(...),
    todolist_uid: str = Path(...),
    task_uid: str = Path(...),
) -> Task:
    """
    Bind/unbind task for current logged user.

    Raises:
        HTTPException: For any unsuccessfully codes.
    """
    todolist = await storage.todolist.get_todolist(todolist_uid)
    if not todolist:
        logging.warning(f'todolist {todolist=} not found')
        raise HTTPException(HTTP_400_BAD_REQUEST, 'todolist not found')

    try:
        task: Task = [
            task_item
            for task_item in todolist.tasks
            if task_item.uid == task_uid
        ][0]
    except IndexError:
        logging.warning(f'task {task_uid=} not found in todolist')
        raise HTTPException(HTTP_400_BAD_REQUEST, 'task not found')

    if lock_status:
        await _lock_handler(task_uid, request.state.current_user.id)

    else:
        await _unlock_handler(task, request.state.current_user.id)

    return await storage.todolist.get_task(task_uid)


async def _lock_handler(task_uid: str, user_id: int):
    ok = await storage.todolist.lock_task(task_uid, user_id)
    if not ok:
        logging.warning('try lock task was already locked')
        raise HTTPException(HTTP_409_CONFLICT, 'already locked')


async def _unlock_handler(task: Task, user_id: int):
    if task.bind_user != user_id:
        logging.warning('try unlock task was bind to another user')
        raise HTTPException(HTTP_400_BAD_REQUEST, 'task locked by another user')

    await storage.todolist.unlock_task(task.uid)
