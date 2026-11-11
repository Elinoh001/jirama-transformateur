from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.controllers import releve_charge as controller
from app.database.connection import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.releve_charge import ReleveChargeCreate, ReleveChargeRead
from app.utils.dependencies import require_admin_or_agent, require_authenticated

router = APIRouter(prefix="/releves-charge", tags=["Suivi de charge"])


@router.get("", response_model=list[ReleveChargeRead])
def list_releves(
    transformateur_id: int | None = Query(default=None, gt=0, description="Historique d'un transformateur"),
    surcharge: bool | None = Query(default=None, description="true = taux > 100 %, false = taux <= 100 %"),
    date_debut: date | None = Query(default=None),
    date_fin: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> list[ReleveChargeRead]:
    return controller.list_releves(db, transformateur_id, surcharge, date_debut, date_fin, skip, limit)


@router.post("", response_model=ReleveChargeRead, status_code=status.HTTP_201_CREATED)
def create_releve(
    data: ReleveChargeCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_admin_or_agent),
) -> ReleveChargeRead:
    return controller.create_releve(db, data, current_user)


@router.get("/{releve_id}", response_model=ReleveChargeRead)
def get_releve(
    releve_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> ReleveChargeRead:
    return controller.get_releve(db, releve_id)
