from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.intervention import StatutIntervention

TYPES_INTERVENTION = {"PREVENTIVE", "CORRECTIVE", "REMPLACEMENT"}


def _normaliser_type(valeur: str | None) -> str | None:
    if valeur is None:
        return valeur
    normalise = valeur.strip().upper().replace(" ", "_")
    if normalise not in TYPES_INTERVENTION:
        raise ValueError(
            f"type invalide, valeurs possibles : {', '.join(sorted(TYPES_INTERVENTION))}"
        )
    return normalise


class InterventionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    transformateur_id: int = Field(gt=0)
    date_intervention: date  # peut être dans le futur (intervention planifiée)
    type: str = Field(default="PREVENTIVE", max_length=50)
    description: str | None = Field(default=None, max_length=2000)
    cout: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    statut: StatutIntervention = StatutIntervention.PLANIFIEE
    # Si absent, le backend utilise le nom de l'utilisateur connecté.
    technicien: str | None = Field(default=None, min_length=1, max_length=150)

    @field_validator("type")
    @classmethod
    def valider_type(cls, v: str) -> str:
        return _normaliser_type(v)


class InterventionUpdate(BaseModel):
    """Le transformateur d'une intervention ne peut pas être changé."""

    model_config = ConfigDict(str_strip_whitespace=True)

    date_intervention: date | None = None
    type: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=2000)
    cout: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    statut: StatutIntervention | None = None
    technicien: str | None = Field(default=None, min_length=1, max_length=150)

    @field_validator("type")
    @classmethod
    def valider_type(cls, v: str | None) -> str | None:
        return _normaliser_type(v)


class InterventionRead(BaseModel):
    id: int
    transformateur_id: int
    transformateur_reference: str
    transformateur_nom: str
    date_intervention: date
    type: str
    description: str | None
    cout: float | None
    statut: StatutIntervention
    technicien: str
    created_at: datetime