from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.security import hash_password, verify_password
from app.models.utilisateur import Utilisateur

# Hash factice, calculé une seule fois : sert à garder le même temps de réponse quand l'email
# n'existe pas (sinon on pourrait deviner quels emails ont un compte grâce à la durée de réponse).
_HASH_FACTICE: str | None = None


def _hash_factice() -> str:
    global _HASH_FACTICE
    if _HASH_FACTICE is None:
        _HASH_FACTICE = hash_password("mot-de-passe-factice-jamais-utilise-1")
    return _HASH_FACTICE


def get_user_by_email(db: Session, email: str) -> Utilisateur | None:
    return db.scalar(select(Utilisateur).where(Utilisateur.email == email.lower().strip()))


def get_user_by_id(db: Session, user_id: int) -> Utilisateur | None:
    return db.get(Utilisateur, user_id)


def authenticate_user(db: Session, email: str, password: str) -> Utilisateur | None:
    """Retourne l'utilisateur si email + mot de passe sont corrects, sinon None."""
    user = get_user_by_email(db, email)
    if user is None:
        verify_password(password, _hash_factice())  # même durée de calcul qu'un vrai compte
        return None
    if not verify_password(password, user.mot_de_passe):
        return None
    return user


def change_password(db: Session, user: Utilisateur, nouveau_mot_de_passe: str) -> None:
    user.mot_de_passe = hash_password(nouveau_mot_de_passe)
    db.commit()
