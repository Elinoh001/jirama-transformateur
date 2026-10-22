from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.security import verify_password
from app.models.utilisateur import Utilisateur


def get_user_by_email(db: Session, email: str) -> Utilisateur | None:
    return db.scalar(select(Utilisateur).where(Utilisateur.email == email.lower().strip()))


def get_user_by_id(db: Session, user_id: int) -> Utilisateur | None:
    return db.get(Utilisateur, user_id)


def authenticate_user(db: Session, email: str, password: str) -> Utilisateur | None:
    """Retourne l'utilisateur si email + mot de passe sont corrects, sinon None."""
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.mot_de_passe):
        return None
    return user