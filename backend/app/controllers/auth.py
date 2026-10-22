from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.security import create_access_token
from app.models.utilisateur import Utilisateur
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.utilisateur import UtilisateurRead
from app.services import auth_service


def login(db: Session, data: LoginRequest) -> TokenResponse:
    user = auth_service.authenticate_user(db, data.email, data.password)

    if user is None:
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

    token = create_access_token(user_id=user.id, role=user.role.value)
    return TokenResponse(access_token=token, user=UtilisateurRead.model_validate(user))


def get_me(current_user: Utilisateur) -> UtilisateurRead:
    return UtilisateurRead.model_validate(current_user)