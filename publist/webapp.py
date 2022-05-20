"""Todolist web app."""
import logging
from http import HTTPStatus
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, RedirectResponse, Response, HTMLResponse

from publist import storage
from publist.schemes import User
from publist.settings import app_settings

app = FastAPI(default_response_class=ORJSONResponse)


@app.middleware('http')
async def sign_in_user_middleware(request: Request, call_next) -> Response:
    """Auth user by cookie value."""
    auth_cookie_value = request.cookies.get(app_settings.auth_cookie_key)

    auth_user: Optional[User] = None
    if auth_cookie_value:
        auth_user = await storage.get_user(uid=auth_cookie_value)
    if not auth_user:
        auth_user = await storage.create_user()

    request.state.current_user = auth_user
    response: Response = await call_next(request)
    response.set_cookie(app_settings.auth_cookie_key, auth_user.auth_uid)

    return response


@app.get('/', response_class=RedirectResponse, status_code=HTTPStatus.TEMPORARY_REDIRECT, tags=['pages'])
async def create_todo_list_page(request: Request):
    """Create new todolist and redirect ro edit page."""
    created_todolist = await storage.create_todolist(request.state.current_user.id)
    return app.url_path_for("edit_todo_list_page", uid=created_todolist.uid)


@app.get('/{uid}/edit', response_class=HTMLResponse, tags=['pages'])
async def edit_todo_list_page(uid: str, request: Request):
    """Show edit todolist page."""
    todolist = await storage.get_todolist(uid)
    if not todolist:
        logging.warning('todolist auth=%s not found', uid)
        return RedirectResponse(app.url_path_for('create_todo_list_page'))

    if todolist.owner_user_id != request.state.current_user.id:
        logging.warning(
            'todolist auth=%s - owner mistake (%s given)',
            uid,
            request.state.current_user.id,
        )
        return RedirectResponse(app.url_path_for('view_todo_list_page', uid=uid))

    # todo use html-template
    return "<!DOCTYPE html><html></html>"


@app.get('/{uid}/view', response_class=HTMLResponse, tags=['pages'])
async def view_todo_list_page(uid: str):
    """Show todolist page with bind buttons."""
    todolist = await storage.get_todolist(uid)
    if not todolist:
        logging.warning('todolist auth=%s not found', uid)
        return RedirectResponse(app.url_path_for("create_todo_list_page"))

    todolist.tasks = [i for i in todolist.tasks if i.title]

    # todo use html-template
    return "<!DOCTYPE html><html></html>"


#
# async def update_task_api(uid: str, task_idx: int, title: str) -> Task:
#     """Update todolist tasks."""
#     # todo test
#     user = _sign_in_user()
#     # todo check todolist ownership
#     # todo update todolist.task title by idx
#     ...
#
#
# async def lock_task_api(task_uid: str, lock_status: bool) -> Task:
#     """Bind task for current logged user."""
#     # todo test
#     user = _sign_in_user()
#     # todo update task.bind_user value by request
#     ...
