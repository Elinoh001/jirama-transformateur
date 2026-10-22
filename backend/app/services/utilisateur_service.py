from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.security import hash_password
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurUpdate


def list_utilisateurs(db: Session, skip: int = 0, limit: int = 200) -> list[Utilisateur]:
    stmt = select(Utilisateur).order_by(Utilisateur.id).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_by_id(db: Session, user_id: int) -> Utilisateur | None:
    return db.get(Utilisateur, user_id)


def get_by_email(db: Session, email: str) -> Utilisateur | None:
    return db.scalar(select(Utilisateur).where(Utilisateur.email == email.lower().strip()))


def create_utilisateur(db: Session, data: UtilisateurCreate) -> Utilisateur:
    user = Utilisateur(
        nom=data.nom,
        prenom=data.prenom,
        email=data.email,
        mot_de_passe=hash_password(data.mot_de_passe),
        role=data.role,
        actif=data.actif,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_utilisateur(db: Session, user: Utilisateur, data: UtilisateurUpdate) -> Utilisateur:
    values = data.model_dump(exclude_unset=True)

    nouveau_mdp = values.pop("mot_de_passe", None)
    if nouveau_mdp:
        user.mot_de_passe = hash_password(nouveau_mdp)

    for champ, valeur in values.items():
        if valeur is None:
            continue
        setattr(user, champ, valeur)

    db.commit()
    db.refresh(user)
    return user


def delete_utilisateur(db: Session, user: Utilisateur) -> None:
    db.delete(user)
    db.commit()