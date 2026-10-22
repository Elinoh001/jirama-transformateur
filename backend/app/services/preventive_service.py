"""
Suivi préventif : calcul de la priorité d'un transformateur par règles simples.
Aucune IA : uniquement des conditions explicites sur l'état et les inspections.

Niveaux : NORMAL < A_SURVEILLER < PRIORITAIRE

Seules les inspections RÉALISÉES comptent : une inspection planifiée n'a pas d'état constaté.
"""
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Iterable, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inspection import Inspection, StatutInspection
from app.models.transformateur import EtatTransformateur, Transformateur

# --- Seuils des règles (modifiables) ---
SEUIL_INSPECTION_ANCIENNE_JOURS = 365  # au-delà : inspection considérée comme ancienne
FENETRE_ANOMALIES_JOURS = 180  # période observée pour compter les anomalies
NB_ANOMALIES_PRIORITAIRE = 2  # nb d'inspections CRITIQUE (dans la fenêtre) => PRIORITAIRE


class NiveauPriorite(str, Enum):
    NORMAL = "NORMAL"
    A_SURVEILLER = "A_SURVEILLER"
    PRIORITAIRE = "PRIORITAIRE"


_RANG = {
    NiveauPriorite.PRIORITAIRE: 0,
    NiveauPriorite.A_SURVEILLER: 1,
    NiveauPriorite.NORMAL: 2,
}


def rang_niveau(niveau: NiveauPriorite) -> int:
    """0 = le plus urgent. Sert à trier les priorités."""
    return _RANG[niveau]


class InspectionLike(Protocol):
    """Tout objet ayant une date et un état (ex: Inspection ORM)."""

    date_inspection: date
    etat: EtatTransformateur | None


@dataclass
class ResultatPriorite:
    niveau: NiveauPriorite
    motifs: list[str] = field(default_factory=list)
    derniere_inspection: date | None = None
    jours_depuis_derniere_inspection: int | None = None
    nb_anomalies_critiques_recentes: int = 0


def calculer_priorite(
    etat: EtatTransformateur,
    inspections: Iterable[InspectionLike],
    aujourdhui: date | None = None,
) -> ResultatPriorite:
    """
    Fonction pure : ne dépend pas de la base de données.
    Retourne le niveau de priorité et la liste des motifs qui l'expliquent.
    """
    aujourdhui = aujourdhui or date.today()

    triees = sorted(
        inspections,
        key=lambda i: (i.date_inspection, getattr(i, "id", 0)),
        reverse=True,
    )
    derniere = triees[0] if triees else None
    jours = (aujourdhui - derniere.date_inspection).days if derniere else None

    debut_fenetre = aujourdhui - timedelta(days=FENETRE_ANOMALIES_JOURS)
    nb_critiques = sum(
        1
        for i in triees
        if i.etat == EtatTransformateur.CRITIQUE and i.date_inspection >= debut_fenetre
    )

    motifs_prioritaire: list[str] = []
    motifs_surveiller: list[str] = []

    # --- Règles PRIORITAIRE ---
    if etat == EtatTransformateur.CRITIQUE:
        motifs_prioritaire.append("Etat du transformateur : CRITIQUE")
    if derniere and derniere.etat == EtatTransformateur.CRITIQUE:
        motifs_prioritaire.append("Dernière inspection : état CRITIQUE")
    if nb_critiques >= NB_ANOMALIES_PRIORITAIRE:
        motifs_prioritaire.append(
            f"{nb_critiques} inspections CRITIQUE sur les {FENETRE_ANOMALIES_JOURS} derniers jours"
        )

    # --- Règles A_SURVEILLER ---
    if etat == EtatTransformateur.A_SURVEILLER:
        motifs_surveiller.append("Etat du transformateur : A SURVEILLER")
    if derniere and derniere.etat == EtatTransformateur.A_SURVEILLER:
        motifs_surveiller.append("Dernière inspection : état A SURVEILLER")
    if derniere is None:
        motifs_surveiller.append("Aucune inspection enregistrée")
    elif jours is not None and jours > SEUIL_INSPECTION_ANCIENNE_JOURS:
        motifs_surveiller.append(
            f"Dernière inspection ancienne ({jours} jours, seuil : {SEUIL_INSPECTION_ANCIENNE_JOURS})"
        )

    # --- Décision : le niveau le plus grave l'emporte ---
    if motifs_prioritaire:
        niveau = NiveauPriorite.PRIORITAIRE
    elif motifs_surveiller:
        niveau = NiveauPriorite.A_SURVEILLER
    else:
        niveau = NiveauPriorite.NORMAL

    motifs = motifs_prioritaire + motifs_surveiller
    if not motifs:
        motifs = ["Etat BON et inspection récente"]

    return ResultatPriorite(
        niveau=niveau,
        motifs=motifs,
        derniere_inspection=derniere.date_inspection if derniere else None,
        jours_depuis_derniere_inspection=jours,
        nb_anomalies_critiques_recentes=nb_critiques,
    )


def evaluer_transformateurs(
    db: Session, transformateurs: list[Transformateur]
) -> dict[int, ResultatPriorite]:
    """Calcule la priorité de plusieurs transformateurs avec UNE seule requête sur les inspections."""
    if not transformateurs:
        return {}

    ids = [t.id for t in transformateurs]
    inspections = db.scalars(
        select(Inspection).where(
            Inspection.transformateur_id.in_(ids),
            Inspection.statut == StatutInspection.REALISEE,
        )
    ).all()

    par_transformateur: dict[int, list[Inspection]] = defaultdict(list)
    for inspection in inspections:
        par_transformateur[inspection.transformateur_id].append(inspection)

    return {t.id: calculer_priorite(t.etat, par_transformateur[t.id]) for t in transformateurs}


def evaluer_transformateur(db: Session, transformateur: Transformateur) -> ResultatPriorite:
    return evaluer_transformateurs(db, [transformateur])[transformateur.id]