"""Todolist web app."""
from http import HTTPStatus
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, RedirectResponse, Response

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
    return f'/{created_todolist.uid}/edit'

# @router_pages.get('/{uid}/edit')
# async def edit_todo_list_page(uid: str):
#     """Show edit todolist page."""
#     # todo test
#     # todo impl
#     # todo fetch todolist by uid
#     ...
#
#
# @router_pages.get('/{uid}/view')
# async def show_todo_list_page(uid: str):
#     """Show todolist page with bind buttons."""
#     # todo test
#     user = _sign_in_user()
#     # todo fetch todolist by uid
#     # todo filter empty tasks
#     ...
#
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
