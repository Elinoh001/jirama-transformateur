from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.controllers import utilisateur as controller
from app.database.connection import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurRead, UtilisateurUpdate
from app.utils.dependencies import require_admin

# Toutes les routes de ce fichier sont réservées à ADMIN.
router = APIRouter(
    prefix="/utilisateurs",
    tags=["Utilisateurs"],
)


@router.get("", response_model=list[UtilisateurRead])
def list_utilisateurs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_admin),
) -> list[UtilisateurRead]:
    return controller.list_utilisateurs(db, skip, limit)


@router.post("", response_model=UtilisateurRead, status_code=status.HTTP_201_CREATED)
def create_utilisateur(
    data: UtilisateurCreate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_admin),
) -> UtilisateurRead:
    return controller.create_utilisateur(db, data)


@router.get("/{user_id}", response_model=UtilisateurRead)
def get_utilisateur(
    user_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(require_admin),
) -> UtilisateurRead:
    return controller.get_utilisateur(db, user_id)


@router.put("/{user_id}", response_model=UtilisateurRead)
def update_utilisateur(
    user_id: int,
    data: UtilisateurUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_admin),
) -> UtilisateurRead:
    return controller.update_utilisateur(db, user_id, data, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_utilisateur(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_admin),
) -> None:
    controller.delete_utilisateur(db, user_id, current_user)