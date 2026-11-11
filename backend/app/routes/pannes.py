from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.controllers import panne as controller
from app.database.connection import get_db
from app.models.panne import GravitePanne, StatutPanne
from app.models.utilisateur import Utilisateur
from app.schemas.panne import PanneCreate, PanneRead, PanneUpdate
from app.utils.dependencies import require_admin_or_agent, require_authenticated

router = APIRouter(prefix="/pannes", tags=["Pannes"])


@router.get("", response_model=list[PanneRead])
def list_pannes(
    transformateur_id: int | None = Query(default=None, gt=0, description="Filtrer par transformateur"),
    statut: StatutPanne | None = Query(default=None, description="SIGNALEE, EN_COURS ou RESOLUE"),
    gravite: GravitePanne | None = Query(default=None),
    active: bool | None = Query(default=None, description="true = non résolues, false = résolues"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> list[PanneRead]:
    return controller.list_pannes(db, transformateur_id, statut, gravite, active, skip, limit)


@router.post("", response_model=PanneRead, status_code=status.HTTP_201_CREATED)
def create_panne(
    data: PanneCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_admin_or_agent),
) -> PanneRead:
    return controller.create_panne(db, data, current_user)


@router.get("/{panne_id}", response_model=PanneRead)
def get_panne(
    panne_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> PanneRead:
    return controller.get_panne(db, panne_id)


@router.put("/{panne_id}", response_model=PanneRead)
def update_panne(
    panne_id: int,
    data: PanneUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_admin_or_agent),
) -> PanneRead:
    return controller.update_panne(db, panne_id, data, current_user)
