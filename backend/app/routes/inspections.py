from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.controllers import inspection as controller
from app.database.connection import get_db
from app.models.inspection import StatutInspection
from app.models.transformateur import EtatTransformateur
from app.models.utilisateur import Utilisateur
from app.schemas.inspection import InspectionCreate, InspectionRead, InspectionUpdate
from app.utils.dependencies import require_admin_or_agent, require_authenticated

router = APIRouter(prefix="/inspections", tags=["Inspections"])


@router.get("", response_model=list[InspectionRead])
def list_inspections(
    transformateur_id: int | None = Query(default=None, gt=0, description="Filtrer par transformateur"),
    etat: EtatTransformateur | None = Query(default=None),
    statut: StatutInspection | None = Query(default=None, description="PLANIFIEE, REALISEE ou ANNULEE"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> list[InspectionRead]:
    return controller.list_inspections(db, transformateur_id, etat, statut, skip, limit)


@router.post("", response_model=InspectionRead, status_code=status.HTTP_201_CREATED)
def create_inspection(
    data: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_admin_or_agent),
) -> InspectionRead:
    return controller.create_inspection(db, data, current_user)


@router.get("/{inspection_id}", response_model=InspectionRead)
def get_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> InspectionRead:
    return controller.get_inspection(db, inspection_id)


@router.put("/{inspection_id}", response_model=InspectionRead)
def update_inspection(
    inspection_id: int,
    data: InspectionUpdate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_admin_or_agent),
) -> InspectionRead:
    return controller.update_inspection(db, inspection_id, data)