from typing import Optional

from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import ORJSONResponse, RedirectResponse, Response

from publist import storage
from publist.schemes import User
from publist.settings import app_settings

app = FastAPI(default_response_class=ORJSONResponse)
router_pages = APIRouter(tags=["html pages"])
router_api = APIRouter(prefix="/api", tags=["api"])


@app.middleware("http")
async def sign_in_user_middleware(request: Request, call_next):
    auth_cookie_value = request.cookies.get(app_settings.auth_cookie_key)
    auth_user: User = await _sign_in_user(auth_cookie_value)
    request.state.current_user = auth_user

    response: Response = await call_next(request)
    response.set_cookie(app_settings.auth_cookie_key, auth_user.auth_uid)
    return response


@router_pages.get('/', response_class=RedirectResponse, status_code=302)
async def create_todo_list_page(request: Request):
    """Create new todolist and redirect ro edit page."""
    # todo test
    created_todolist = await storage.create_todolist(request.state.current_user.id, app_settings.todolist_ttl_days)
    return f'/{created_todolist.owner_user_id}/edit'


async def _sign_in_user(auth_cookie_value: Optional[str]) -> User:
    # todo test
    auth_user = None
    if auth_cookie_value:
        auth_user = await storage.get_user(uid=auth_cookie_value)

    if not auth_user:
        auth_user = await storage.create_user()

    return auth_user
#
#
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


app.include_router(router_pages)
app.include_router(router_api)
