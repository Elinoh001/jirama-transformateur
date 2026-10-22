from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.controllers import transformateur as controller
from app.database.connection import get_db
from app.models.transformateur import EtatTransformateur
from app.models.utilisateur import Utilisateur
from app.schemas.transformateur import (
    HistoriqueRead,
    PrioriteItem,
    TransformateurCreate,
    TransformateurRead,
    TransformateurUpdate,
)
from app.services.preventive_service import NiveauPriorite
from app.utils.dependencies import require_admin, require_authenticated

router = APIRouter(prefix="/transformateurs", tags=["Transformateurs"])


@router.get("", response_model=list[TransformateurRead])
def list_transformateurs(
    search: str | None = Query(default=None, description="Recherche sur référence ou nom"),
    etat: EtatTransformateur | None = Query(default=None),
    actif: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> list[TransformateurRead]:
    return controller.list_transformateurs(db, search, etat, actif, skip, limit)


@router.post("", response_model=TransformateurRead, status_code=status.HTTP_201_CREATED)
def create_transformateur(
    data: TransformateurCreate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_admin),
) -> TransformateurRead:
    return controller.create_transformateur(db, data)


# IMPORTANT : cette route doit rester AVANT "/{transformateur_id}",
# sinon FastAPI essaierait de lire "priorites" comme un identifiant entier.
@router.get("/priorites", response_model=list[PrioriteItem])
def list_priorites(
    niveau: NiveauPriorite | None = Query(default=None, description="Filtrer par niveau"),
    inclure_inactifs: bool = Query(default=False),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> list[PrioriteItem]:
    return controller.list_priorites(db, niveau, inclure_inactifs)


@router.get("/{transformateur_id}", response_model=TransformateurRead)
def get_transformateur(
    transformateur_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> TransformateurRead:
    return controller.get_transformateur(db, transformateur_id)


@router.get("/{transformateur_id}/historique", response_model=HistoriqueRead)
def get_historique(
    transformateur_id: int,
    ordre: Literal["asc", "desc"] = Query(default="desc", description="desc = plus récent d'abord"),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_authenticated),
) -> HistoriqueRead:
    return controller.get_historique(db, transformateur_id, ordre)


@router.put("/{transformateur_id}", response_model=TransformateurRead)
def update_transformateur(
    transformateur_id: int,
    data: TransformateurUpdate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_admin),
) -> TransformateurRead:
    return controller.update_transformateur(db, transformateur_id, data)


@router.delete("/{transformateur_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transformateur(
    transformateur_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_admin),
) -> None:
    controller.delete_transformateur(db, transformateur_id)