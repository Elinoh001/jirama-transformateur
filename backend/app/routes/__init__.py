from fastapi import APIRouter

from app.routes import (
    auth,
    dashboard,
    health,
    inspections,
    interventions,
    transformateurs,
    utilisateurs,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(utilisateurs.router)
api_router.include_router(transformateurs.router)
api_router.include_router(inspections.router)
api_router.include_router(interventions.router)
api_router.include_router(dashboard.router)