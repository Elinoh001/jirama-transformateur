import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.security import create_access_token, verify_password
from app.models.utilisateur import Utilisateur
from app.schemas.auth import ChangePasswordRequest, LoginRequest, MessageResponse, TokenResponse
from app.schemas.utilisateur import UtilisateurRead
from app.services import auth_service
from app.services.login_guard import login_guard

logger = logging.getLogger("uvicorn.error")


def _trop_de_tentatives(secondes: int) -> HTTPException:
    minutes = max(1, round(secondes / 60))
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=f"Trop de tentatives de connexion. Réessayez dans {minutes} minute(s).",
        headers={"Retry-After": str(secondes)},
    )


def login(db: Session, data: LoginRequest, client_ip: str = "inconnue") -> TokenResponse:
    # 1) Connexion bloquée après trop d'échecs (même un bon mot de passe est refusé pendant le blocage).
    attente = login_guard.secondes_restantes(client_ip, data.email)
    if attente > 0:
        raise _trop_de_tentatives(attente)

    user = auth_service.authenticate_user(db, data.email, data.password)

    if user is None:
        login_guard.enregistrer_echec(client_ip, data.email)
        logger.warning("Échec de connexion pour %s depuis %s", data.email, client_ip)
        # Message volontairement identique pour email inconnu et mauvais mot de passe.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    if not user.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé",
        )

    login_guard.reinitialiser_couple(client_ip, data.email)
    token = create_access_token(user_id=user.id, role=user.role.value)
    return TokenResponse(access_token=token, user=UtilisateurRead.model_validate(user))


def get_me(current_user: Utilisateur) -> UtilisateurRead:
    return UtilisateurRead.model_validate(current_user)


def change_password(
    db: Session, current_user: Utilisateur, data: ChangePasswordRequest, client_ip: str = "inconnue"
) -> MessageResponse:
    """Changement de son propre mot de passe : l'ancien est exigé (vol de session impossible sans lui)."""
    cle = f"mdp-utilisateur-{current_user.id}"
    attente = login_guard.secondes_restantes(client_ip, cle)
    if attente > 0:
        raise _trop_de_tentatives(attente)

    # 400 et non 401 : un 401 déconnecterait l'utilisateur côté frontend.
    if not verify_password(data.ancien_mot_de_passe, current_user.mot_de_passe):
        login_guard.enregistrer_echec(client_ip, cle)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Le mot de passe actuel est incorrect")

    if data.nouveau_mot_de_passe == data.ancien_mot_de_passe:
        raise HTTPException(422, "Le nouveau mot de passe doit être différent de l'ancien")

    auth_service.change_password(db, current_user, data.nouveau_mot_de_passe)
    login_guard.reinitialiser_couple(client_ip, cle)
    return MessageResponse(message="Mot de passe modifié avec succès")
