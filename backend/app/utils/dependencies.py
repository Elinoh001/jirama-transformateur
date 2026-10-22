from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config.security import decode_access_token
from app.database.connection import get_db
from app.models.utilisateur import RoleUtilisateur, Utilisateur
from app.services import auth_service

# auto_error=False : on gère nous-mêmes l'erreur pour retourner 401 (et non 403).
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Utilisateur:
    """Extrait l'utilisateur connecté à partir du header Authorization: Bearer <token>."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentification requise ou token invalide",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise unauthorized

    try:
        user_id = int(payload.get("sub", ""))
    except (TypeError, ValueError):
        raise unauthorized

    user = auth_service.get_user_by_id(db, user_id)
    if user is None or not user.actif:
        raise unauthorized

    return user


def require_roles(*roles: RoleUtilisateur) -> Callable[..., Utilisateur]:
    """
    Fabrique une dépendance qui n'autorise que les rôles indiqués.
    Le rôle est lu en base (pas dans le token) : un changement de rôle est effectif immédiatement.

    Exemple : Depends(require_roles(RoleUtilisateur.ADMIN))
    """

    def checker(current_user: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé : permissions insuffisantes",
            )
        return current_user

    return checker


# Raccourcis de permissions réutilisés par les routes.
# Tout utilisateur connecté et actif (ADMIN, SUPERVISEUR, AGENT) : consultation.
require_authenticated = require_roles(
    RoleUtilisateur.ADMIN, RoleUtilisateur.SUPERVISEUR, RoleUtilisateur.AGENT
)
# ADMIN uniquement : gestion des utilisateurs, des transformateurs.
require_admin = require_roles(RoleUtilisateur.ADMIN)
# ADMIN + AGENT : création/modification des inspections et interventions.
require_admin_or_agent = require_roles(RoleUtilisateur.ADMIN, RoleUtilisateur.AGENT)
# ADMIN + SUPERVISEUR : dashboard et statistiques.
require_admin_or_superviseur = require_roles(RoleUtilisateur.ADMIN, RoleUtilisateur.SUPERVISEUR)