"""HTML pages for webapp."""

import logging
from http import HTTPStatus

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from publist import storage
from publist.settings import app_settings

router = APIRouter(tags=['pages'], default_response_class=HTMLResponse)
templates = Jinja2Templates(directory=app_settings.app_path.joinpath('templates'))


@router.get('/', response_class=RedirectResponse, status_code=HTTPStatus.TEMPORARY_REDIRECT)
async def create_todo_list_page(request: Request):
    """Create new todolist and redirect ro edit page."""
    created_todolist = await storage.todolist.create_todolist(request.state.current_user.id)
    logging.info(f'create new todolist {created_todolist.uid=}')
    return router.url_path_for('edit_todo_list_page', uid=created_todolist.uid)


@router.get('/{uid}/edit')
async def edit_todo_list_page(uid: str, request: Request):
    """Show edit todolist page."""
    todolist = await storage.todolist.get_todolist(uid)
    if not todolist:
        logging.warning(f'todolist {uid=} not found')
        return RedirectResponse(router.url_path_for('create_todo_list_page'))

    if todolist.owner_user_id != request.state.current_user.id:
        logging.warning('todolist {0} - owner mistake ({1} given)'.format(
            uid,
            request.state.current_user.id,
        ))
        return RedirectResponse(router.url_path_for('view_todo_list_page', uid=uid))

    return templates.TemplateResponse('edit.html', {
        'request': request,
        'todolist': todolist,
        'empty_task_count': max(
            app_settings.empty_tasks_on_page_min,
            app_settings.empty_tasks_on_page_max - len(todolist.tasks),
        ),
    })


@router.get('/{uid}/view')
async def view_todo_list_page(uid: str, request: Request):
    """Show todolist page with bind buttons."""
    todolist = await storage.todolist.get_todolist(uid)
    if not todolist:
        logging.warning(f'todolist {uid=} not found')
        return RedirectResponse(router.url_path_for('create_todo_list_page'))

    todolist.tasks = [task for task in todolist.tasks if task.title]

    return templates.TemplateResponse('view.html', {
        'request': request,
        'todolist': todolist,
        'current_user_id': request.state.current_user.id,
    })
