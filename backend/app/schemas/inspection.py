from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.inspection import EtatHuile, StatutInspection
from app.models.transformateur import EtatTransformateur

TYPES_INSPECTION = {"ROUTINE", "VISUELLE", "THERMIQUE", "POST_INCIDENT"}


def _normaliser_type(valeur: str | None) -> str | None:
    if valeur is None:
        return valeur
    normalise = valeur.strip().upper().replace(" ", "_")
    if normalise not in TYPES_INSPECTION:
        raise ValueError(f"type invalide, valeurs possibles : {', '.join(sorted(TYPES_INSPECTION))}")
    return normalise


class InspectionCreate(BaseModel):
    """
    - REALISEE (défaut) : compte-rendu d'une inspection faite. État constaté obligatoire,
      date aujourd'hui ou passée.
    - PLANIFIEE : inspection programmée. Date aujourd'hui ou future, pas d'état constaté.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    transformateur_id: int = Field(gt=0)
    date_inspection: date
    type: str = Field(default="ROUTINE", max_length=50)
    statut: StatutInspection = StatutInspection.REALISEE
    etat: EtatTransformateur | None = None
    etat_huile: EtatHuile | None = None
    observation: str | None = Field(default=None, max_length=2000)
    # Si absent, le backend utilise le nom de l'utilisateur connecté.
    technicien: str | None = Field(default=None, min_length=1, max_length=150)

    @field_validator("type")
    @classmethod
    def valider_type(cls, v: str) -> str:
        return _normaliser_type(v)

    @model_validator(mode="after")
    def valider_coherence(self) -> "InspectionCreate":
        if self.statut == StatutInspection.ANNULEE:
            raise ValueError("Une inspection ne peut pas être créée avec le statut ANNULEE")

        if self.statut == StatutInspection.REALISEE:
            if self.etat is None:
                raise ValueError("L'état constaté est obligatoire pour une inspection réalisée")
            if self.date_inspection > date.today():
                raise ValueError("La date d'une inspection réalisée ne peut pas être dans le futur")
        else:  # PLANIFIEE
            if self.date_inspection < date.today():
                raise ValueError("Impossible de planifier une inspection à une date passée")
            self.etat = None
            self.etat_huile = None
        return self


class InspectionUpdate(BaseModel):
    """Le transformateur d'une inspection ne peut pas être changé. Les règles de cohérence
    (statut, état, date) sont vérifiées par le contrôleur, qui connaît l'inspection existante."""

    model_config = ConfigDict(str_strip_whitespace=True)

    date_inspection: date | None = None
    type: str | None = Field(default=None, max_length=50)
    statut: StatutInspection | None = None
    etat: EtatTransformateur | None = None
    etat_huile: EtatHuile | None = None
    observation: str | None = Field(default=None, max_length=2000)
    technicien: str | None = Field(default=None, min_length=1, max_length=150)

    @field_validator("type")
    @classmethod
    def valider_type(cls, v: str | None) -> str | None:
        return _normaliser_type(v)


class InspectionRead(BaseModel):
    id: int
    transformateur_id: int
    transformateur_reference: str
    transformateur_nom: str
    date_inspection: date
    type: str
    statut: StatutInspection
    etat: EtatTransformateur | None
    etat_huile: EtatHuile | None
    observation: str | None
    technicien: str
    created_at: datetime