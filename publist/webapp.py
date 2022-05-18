from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse, RedirectResponse

from publist import storage
from publist.schemes import User, Task
from publist.settings import app_settings

router_pages = APIRouter(tags=["html pages"])
router_api = APIRouter(prefix="/api", tags=["api"])


@router_pages.get('/', response_class=RedirectResponse, status_code=302)
async def create_todo_list_page():
    """Create new todolist and redirect ro edit page."""
    # todo test
    user = await _sign_in_user()
    created_todolist = await storage.create_todolist(user.id, app_settings.todolist_ttl_days)
    return f'/{created_todolist.owner_user_id}/edit'


async def _sign_in_user() -> User:
    # todo test
    # todo create new user-auth or sign-in by cookie value
    ...


@router_pages.get('/{uid}/edit')
async def edit_todo_list_page(uid: str):
    """Show edit todolist page."""
    user = _sign_in_user()
    # todo test
    # todo impl
    # todo fetch todolist by uid
    ...


@router_pages.get('/{uid}/view')
async def show_todo_list_page(uid: str):
    """Show todolist page with bind buttons."""
    # todo test
    user = _sign_in_user()
    # todo fetch todolist by uid
    # todo filter empty tasks
    ...


async def update_task_api(uid: str, task_idx: int, title: str) -> Task:
    """Update todolist tasks."""
    # todo test
    user = _sign_in_user()
    # todo check todolist ownership
    # todo update todolist.task title by idx
    ...


async def lock_task_api(task_uid: str, lock_status: bool) -> Task:
    """Bind task for current logged user."""
    # todo test
    user = _sign_in_user()
    # todo update task.bind_user value by request
    ...


app = FastAPI(default_response_class=ORJSONResponse)
app.include_router(router_pages)
app.include_router(router_api)
