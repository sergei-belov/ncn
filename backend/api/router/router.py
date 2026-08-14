from fastapi import APIRouter

from api.router.agents import router as agents_router
from api.router.auth import router as auth_router
from api.router.authorization import router as authorization_router
from api.router.board import router as board_router
from api.router.epics import router as epics_router
from api.router.projects import router as projects_router
from api.router.states import router as states_router
from api.router.work_items import router as work_items_router
from api.services import Services


router = APIRouter()
router.include_router(Services.healthcheck_router())
router.include_router(auth_router)
router.include_router(authorization_router)
router.include_router(projects_router)
router.include_router(agents_router)
router.include_router(states_router)
router.include_router(work_items_router)
router.include_router(board_router)
router.include_router(epics_router)
