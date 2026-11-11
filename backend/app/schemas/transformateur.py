from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.config.referentiels import (
    PERIODICITE_INSPECTION_MOIS_DEFAUT,
    normaliser_secteur,
    point_dans_zone,
)
from app.models.panne import GravitePanne
from app.models.transformateur import EtatTransformateur, NiveauHuile
from app.services.preventive_service import NiveauPriorite
from app.services.statut_service import StatutOperationnel

MSG_HORS_ZONE = "Coordonnées hors de la zone d'Antsirabe"


class TransformateurCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    reference: str = Field(min_length=1, max_length=50)
    nom: str = Field(min_length=1, max_length=150)
    secteur: str = Field(min_length=1, max_length=100, description="Quartier / secteur d'Antsirabe")
    puissance: float = Field(gt=0, description="Puissance nominale en kVA")
    tension_mt: float = Field(default=20.0, gt=0, description="Tension MT en kV")
    tension_bt: float = Field(default=400.0, gt=0, description="Tension BT en V")
    type_huile: str | None = Field(default=None, max_length=100)
    niveau_huile: NiveauHuile = NiveauHuile.NORMAL
    date_installation: date | None = None
    etat: EtatTransformateur = EtatTransformateur.BON
    periodicite_inspection_mois: int = Field(
        default=PERIODICITE_INSPECTION_MOIS_DEFAUT, ge=1, le=60
    )
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    actif: bool = True

    @field_validator("secteur")
    @classmethod
    def valider_secteur(cls, v: str) -> str:
        return normaliser_secteur(v)

    @model_validator(mode="after")
    def valider_zone(self) -> "TransformateurCreate":
        if not point_dans_zone(self.latitude, self.longitude):
            raise ValueError(MSG_HORS_ZONE)
        return self


class TransformateurUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    reference: str | None = Field(default=None, min_length=1, max_length=50)
    nom: str | None = Field(default=None, min_length=1, max_length=150)
    secteur: str | None = Field(default=None, min_length=1, max_length=100)
    puissance: float | None = Field(default=None, gt=0)
    tension_mt: float | None = Field(default=None, gt=0)
    tension_bt: float | None = Field(default=None, gt=0)
    type_huile: str | None = Field(default=None, max_length=100)
    niveau_huile: NiveauHuile | None = None
    date_installation: date | None = None
    etat: EtatTransformateur | None = None
    periodicite_inspection_mois: int | None = Field(default=None, ge=1, le=60)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    actif: bool | None = None

    @field_validator("secteur")
    @classmethod
    def valider_secteur(cls, v: str | None) -> str | None:
        return normaliser_secteur(v) if v is not None else None

    @model_validator(mode="after")
    def valider_coordonnees(self) -> "TransformateurUpdate":
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude et longitude doivent être fournies ensemble")
        if self.latitude is not None and not point_dans_zone(self.latitude, self.longitude):
            raise ValueError(MSG_HORS_ZONE)
        return self


class TransformateurRead(BaseModel):
    id: int
    reference: str
    nom: str
    secteur: str
    puissance: float
    tension_mt: float
    tension_bt: float
    type_huile: str | None
    niveau_huile: NiveauHuile
    date_installation: date | None
    etat: EtatTransformateur
    periodicite_inspection_mois: int
    # Prochaine inspection PRÉVUE : date planifiée si elle existe, sinon échéance théorique
    prochaine_inspection: date | None
    latitude: float
    longitude: float
    actif: bool
    created_at: datetime
    updated_at: datetime
    # Suivi préventif (calculé automatiquement, jamais stocké en base)
    priorite: NiveauPriorite | None = None
    priorite_motifs: list[str] = Field(default_factory=list)
    derniere_inspection: date | None = None  # dernière inspection réellement réalisée
    echeance_theorique: date | None = None  # dernière réalisée + périodicité
    prochaine_inspection_planifiee: date | None = None  # inspection planifiée la plus proche
    inspection_en_retard: bool = False
    jours_retard_inspection: int = 0
    # Situation opérationnelle (calculée à partir des pannes, interventions et du dernier relevé)
    statut_operationnel: StatutOperationnel | None = None
    nb_pannes_actives: int = 0
    taux_charge: float | None = None  # % du dernier relevé de charge, None si aucun relevé


class PrioriteItem(BaseModel):
    """Ligne de la liste des priorités (tableau de bord et carte)."""

    transformateur_id: int
    reference: str
    nom: str
    puissance: float
    etat: EtatTransformateur
    actif: bool
    latitude: float
    longitude: float
    niveau: NiveauPriorite
    motifs: list[str]
    derniere_inspection: date | None
    jours_depuis_derniere_inspection: int | None
    jours_retard_inspection: int = 0


class HistoriqueEvenement(BaseModel):
    """Un événement de la chronologie : inspection, intervention ou panne."""

    evenement: Literal["INSPECTION", "INTERVENTION", "PANNE"]
    id: int
    date_evenement: date
    type: str
    resume: str | None = None
    technicien: str  # pour une panne : la personne qui l'a signalée
    etat: EtatTransformateur | None = None  # inspections réalisées uniquement
    statut: str | None = None  # statut de l'inspection, de l'intervention ou de la panne
    gravite: GravitePanne | None = None  # pannes uniquement
    cout: float | None = None  # interventions uniquement


class ProcheItem(BaseModel):
    """Résultat d'une recherche par rayon (PostGIS ST_DWithin / ST_Distance)."""

    transformateur_id: int
    reference: str
    nom: str
    secteur: str
    distance_m: float
    latitude: float
    longitude: float
    statut_operationnel: StatutOperationnel


class HistoriqueRead(BaseModel):
    transformateur: TransformateurRead
    total: int
    evenements: list[HistoriqueEvenement]