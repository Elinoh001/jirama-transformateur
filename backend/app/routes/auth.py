from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers import auth as auth_controller
from app.database.connection import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.utilisateur import UtilisateurRead
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_controller.login(db, data)


@router.get("/me", response_model=UtilisateurRead)
def me(current_user: Utilisateur = Depends(get_current_user)) -> UtilisateurRead:
    return auth_controller.get_me(current_user)