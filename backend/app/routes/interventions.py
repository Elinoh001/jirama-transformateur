from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.controllers import intervention as controller
from app.database.connection import get_db
from app.models.intervention import StatutIntervention
from app.models.utilisateur import Utilisateur
from app.schemas.intervention import InterventionCreate, InterventionRead, InterventionUpdate
from app.utils.dependencies import require_admin_or_agent, require_authenticated

router = APIRouter(prefix="/interventions", tags=["Interventions"])


@router.get("", response_model=list[InterventionRead])
def list_interventions(
    transformateur_id: int | None = Query(default=None, gt=0, description="Filtrer par transformateur"),
    statut: StatutIntervention | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> list[InterventionRead]:
    return controller.list_interventions(db, transformateur_id, statut, skip, limit)


@router.post("", response_model=InterventionRead, status_code=status.HTTP_201_CREATED)
def create_intervention(
    data: InterventionCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_admin_or_agent),
) -> InterventionRead:
    return controller.create_intervention(db, data, current_user)


@router.get("/{intervention_id}", response_model=InterventionRead)
def get_intervention(
    intervention_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> InterventionRead:
    return controller.get_intervention(db, intervention_id)


@router.put("/{intervention_id}", response_model=InterventionRead)
def update_intervention(
    intervention_id: int,
    data: InterventionUpdate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_admin_or_agent),
) -> InterventionRead:
    return controller.update_intervention(db, intervention_id, data)