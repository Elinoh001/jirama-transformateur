from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

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


class UtilisateurCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    prenom: str = Field(min_length=1, max_length=100)
    email: EmailLocal
    mot_de_passe: str = Field(min_length=8, max_length=72)
    role: RoleUtilisateur = RoleUtilisateur.AGENT
    actif: bool = True


class UtilisateurUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    prenom: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailLocal | None = None
    mot_de_passe: str | None = Field(default=None, min_length=8, max_length=72)
    role: RoleUtilisateur | None = None
    actif: bool | None = None


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