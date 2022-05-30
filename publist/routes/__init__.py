"""All webapp routes here."""

from fastapi import APIRouter

from publist.routes import api, pages

router = APIRouter()
router.include_router(pages.router)
router.include_router(api.router)
