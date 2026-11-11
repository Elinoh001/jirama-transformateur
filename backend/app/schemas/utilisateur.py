from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.models.utilisateur import RoleUtilisateur

# Validation d'email simple (accepte aussi les domaines .local utilisés en développement).
EmailLocal = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    ),
]


def valider_force_mot_de_passe(valeur: str) -> str:
    """
    Politique de mot de passe : 8 caractères minimum, au moins une lettre et un chiffre.
    bcrypt ne lit que les 72 premiers OCTETS : un mot de passe plus long serait tronqué en silence.
    """
    if len(valeur) < 8:
        raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
    if len(valeur.encode("utf-8")) > 72:
        raise ValueError("Le mot de passe est trop long (72 octets maximum)")
    if not any(c.isalpha() for c in valeur) or not any(c.isdigit() for c in valeur):
        raise ValueError("Le mot de passe doit contenir au moins une lettre et un chiffre")
    return valeur


class UtilisateurCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    prenom: str = Field(min_length=1, max_length=100)
    email: EmailLocal
    mot_de_passe: str = Field(min_length=8, max_length=72)
    role: RoleUtilisateur = RoleUtilisateur.AGENT
    actif: bool = True

    @field_validator("mot_de_passe")
    @classmethod
    def verifier_mot_de_passe(cls, v: str) -> str:
        return valider_force_mot_de_passe(v)


class UtilisateurUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    prenom: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailLocal | None = None
    mot_de_passe: str | None = Field(default=None, min_length=8, max_length=72)
    role: RoleUtilisateur | None = None
    actif: bool | None = None

    @field_validator("mot_de_passe")
    @classmethod
    def verifier_mot_de_passe(cls, v: str | None) -> str | None:
        return valider_force_mot_de_passe(v) if v is not None else v


class UtilisateurRead(BaseModel):
    """Représentation publique d'un utilisateur : jamais de mot de passe."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    prenom: str
    email: str
    role: RoleUtilisateur
    actif: bool
    created_at: datetime
    updated_at: datetime