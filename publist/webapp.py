"""Todolist web app."""
import logging
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from publist import routes, schemes, storage
from publist.settings import app_settings

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.mount(
    '/static',
    StaticFiles(directory=app_settings.app_path.joinpath('static')),
    name='static',
)
app.include_router(routes.router)


@app.middleware('http')
async def sign_in_user_middleware(request: Request, call_next) -> Response:
    """Auth user by cookie value."""
    auth_cookie_value = request.cookies.get(app_settings.auth_cookie_key)

    auth_user: Optional[schemes.User] = None
    if auth_cookie_value:
        auth_user = await storage.user.get_user(uid=auth_cookie_value)
    if not auth_user:
        auth_user = await storage.user.create_user()

    request.state.current_user = auth_user
    response: Response = await call_next(request)
    response.set_cookie(app_settings.auth_cookie_key, auth_user.auth_uid)

    return response
