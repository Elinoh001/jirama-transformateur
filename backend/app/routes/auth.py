from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.controllers import auth as auth_controller
from app.database.connection import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.auth import ChangePasswordRequest, LoginRequest, MessageResponse, TokenResponse
from app.schemas.utilisateur import UtilisateurRead
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentification"])


def _ip(request: Request) -> str:
    """Adresse IP du client (on ne fait pas confiance à X-Forwarded-For, falsifiable)."""
    return request.client.host if request.client else "inconnue"


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_controller.login(db, data, _ip(request))


@router.get("/me", response_model=UtilisateurRead)
def me(current_user: Utilisateur = Depends(get_current_user)) -> UtilisateurRead:
    return auth_controller.get_me(current_user)


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    data: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
) -> MessageResponse:
    """Permet à tout utilisateur connecté de changer son propre mot de passe."""
    return auth_controller.change_password(db, current_user, data, _ip(request))
