from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurRead, UtilisateurUpdate
from app.services import utilisateur_service


def _get_or_404(db: Session, user_id: int) -> Utilisateur:
    user = utilisateur_service.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilisateur introuvable")
    return user


def list_utilisateurs(db: Session, skip: int, limit: int) -> list[UtilisateurRead]:
    users = utilisateur_service.list_utilisateurs(db, skip, limit)
    return [UtilisateurRead.model_validate(u) for u in users]


def get_utilisateur(db: Session, user_id: int) -> UtilisateurRead:
    return UtilisateurRead.model_validate(_get_or_404(db, user_id))


def create_utilisateur(db: Session, data: UtilisateurCreate) -> UtilisateurRead:
    if utilisateur_service.get_by_email(db, data.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Cet email est déjà utilisé")
    return UtilisateurRead.model_validate(utilisateur_service.create_utilisateur(db, data))


def update_utilisateur(
    db: Session, user_id: int, data: UtilisateurUpdate, current_user: Utilisateur
) -> UtilisateurRead:
    user = _get_or_404(db, user_id)

    # Empêche l'admin de se bloquer lui-même.
    if user.id == current_user.id:
        if data.actif is False:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Vous ne pouvez pas désactiver votre propre compte"
            )
        if data.role is not None and data.role != user.role:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Vous ne pouvez pas modifier votre propre rôle"
            )

    if data.email and data.email != user.email:
        if utilisateur_service.get_by_email(db, data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Cet email est déjà utilisé")

    return UtilisateurRead.model_validate(utilisateur_service.update_utilisateur(db, user, data))


def delete_utilisateur(db: Session, user_id: int, current_user: Utilisateur) -> None:
    user = _get_or_404(db, user_id)
    if user.id == current_user.id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Vous ne pouvez pas supprimer votre propre compte"
        )
    utilisateur_service.delete_utilisateur(db, user)