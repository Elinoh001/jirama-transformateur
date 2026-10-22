from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.controllers import dashboard as controller
from app.database.connection import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.dashboard import DashboardStatistics
from app.schemas.transformateur import PrioriteItem
from app.services.preventive_service import NiveauPriorite
from app.utils.dependencies import require_admin_or_superviseur, require_authenticated

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/statistics", response_model=DashboardStatistics)
def get_statistics(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_admin_or_superviseur),
) -> DashboardStatistics:
    return controller.get_statistics(db)


@router.get("/priorities", response_model=list[PrioriteItem])
def get_priorities(
    niveau: NiveauPriorite | None = Query(default=None, description="Filtrer par niveau"),
    inclure_normal: bool = Query(default=False, description="Inclure les niveaux NORMAL"),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> list[PrioriteItem]:
    return controller.get_priorities(db, niveau, inclure_normal, limit)