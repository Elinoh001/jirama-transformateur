"""
Gestion rigoureuse des échéances d'inspection d'un transformateur.

Trois dates sont DISTINGUÉES (elles ne sont jamais mélangées) :

  1. dernière inspection RÉALISÉE : date de la dernière inspection réellement effectuée.
     Elle est lue dans l'historique, donc jamais perdue ni écrasée.

  2. échéance THÉORIQUE : dernière inspection réalisée + périodicité (en mois).
     Sans inspection réalisée, on part de la date d'enregistrement du transformateur.
     C'est la date limite réglementaire : une planification ne la repousse pas.

  3. prochaine inspection PLANIFIÉE : la plus ancienne inspection au statut PLANIFIEE.
     Si elle est dans le passé, elle n'a pas été réalisée : elle est en retard.

La PROCHAINE INSPECTION PRÉVUE (colonne `transformateurs.prochaine_inspection`) vaut :
  - la date planifiée s'il existe une inspection planifiée ;
  - sinon l'échéance théorique.
Elle est recalculée à chaque création, report, annulation ou réalisation d'une inspection.

RETARD : un transformateur est en retard si
  - son échéance théorique est dépassée, OU
  - une inspection planifiée est restée sans suite après sa date.
Le nombre de jours de retard est le plus grand des deux écarts.
"""
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Literal, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inspection import Inspection, StatutInspection
from app.models.transformateur import Transformateur
from app.utils.dates import ajouter_mois

# Deux inspections planifiées du même type, sur le même transformateur, espacées de moins
# de ce nombre de jours, appartiennent à la même période : c'est un doublon.
PERIODE_DOUBLON_JOURS = 30


class InspectionPlanning(Protocol):
    date_inspection: date
    statut: StatutInspection


@dataclass
class SituationEcheance:
    derniere_realisee: date | None
    echeance_theorique: date
    prochaine_planifiee: date | None
    prochaine_prevue: date
    source: Literal["PLANIFIEE", "THEORIQUE"]
    jours_retard: int  # 0 = pas en retard

    @property
    def en_retard(self) -> bool:
        return self.jours_retard > 0


def calculer_echeance(
    periodicite_mois: int,
    date_reference: date,
    inspections: Iterable[InspectionPlanning],
    aujourdhui: date | None = None,
) -> SituationEcheance:
    """
    Fonction pure (sans base de données), facile à tester et à expliquer.
    `date_reference` : date d'enregistrement du transformateur, utilisée s'il n'a encore
    aucune inspection réalisée. Les inspections ANNULEE sont ignorées.
    """
    aujourdhui = aujourdhui or date.today()
    inspections = list(inspections)

    realisees = [i.date_inspection for i in inspections if i.statut == StatutInspection.REALISEE]
    planifiees = sorted(i.date_inspection for i in inspections if i.statut == StatutInspection.PLANIFIEE)

    derniere = max(realisees) if realisees else None
    theorique = ajouter_mois(derniere or date_reference, periodicite_mois)
    planifiee = planifiees[0] if planifiees else None

    retards = []
    if theorique < aujourdhui:
        retards.append((aujourdhui - theorique).days)
    if planifiee is not None and planifiee < aujourdhui:
        retards.append((aujourdhui - planifiee).days)

    return SituationEcheance(
        derniere_realisee=derniere,
        echeance_theorique=theorique,
        prochaine_planifiee=planifiee,
        prochaine_prevue=planifiee or theorique,
        source="PLANIFIEE" if planifiee else "THEORIQUE",
        jours_retard=max(retards, default=0),
    )


def _date_reference(transformateur: Transformateur) -> date:
    """Date d'entrée du transformateur dans le système (repli : aujourd'hui avant le premier commit)."""
    return transformateur.created_at.date() if transformateur.created_at else date.today()


def evaluer_echeances(
    db: Session, transformateurs: list[Transformateur], aujourdhui: date | None = None
) -> dict[int, SituationEcheance]:
    """Situation d'échéance de plusieurs transformateurs avec une seule requête SQL."""
    if not transformateurs:
        return {}

    ids = [t.id for t in transformateurs]
    inspections = db.scalars(
        select(Inspection).where(
            Inspection.transformateur_id.in_(ids),
            Inspection.statut.in_([StatutInspection.REALISEE, StatutInspection.PLANIFIEE]),
        )
    ).all()
    par_transformateur: dict[int, list[Inspection]] = defaultdict(list)
    for inspection in inspections:
        par_transformateur[inspection.transformateur_id].append(inspection)

    return {
        t.id: calculer_echeance(
            t.periodicite_inspection_mois, _date_reference(t), par_transformateur[t.id], aujourdhui
        )
        for t in transformateurs
    }


def synchroniser_prochaine_inspection(db: Session, transformateur: Transformateur) -> SituationEcheance:
    """
    Recalcule la prochaine inspection prévue du transformateur et l'enregistre (sans commit).
    Les modifications en attente doivent avoir été envoyées avec db.flush() : l'autoflush
    est désactivé dans ce projet.
    """
    situation = evaluer_echeances(db, [transformateur])[transformateur.id]
    transformateur.prochaine_inspection = situation.prochaine_prevue
    return situation


def verrouiller_transformateur(db: Session, transformateur_id: int) -> None:
    """
    Verrou de ligne PostgreSQL (SELECT ... FOR UPDATE) tenu jusqu'au commit.
    Deux requêtes simultanées de planification pour un même transformateur passent donc
    l'une après l'autre, et la détection des doublons reste fiable.
    """
    db.execute(select(Transformateur.id).where(Transformateur.id == transformateur_id).with_for_update())


def trouver_planification_proche(
    db: Session,
    transformateur_id: int,
    type_inspection: str,
    date_inspection: date,
    exclure_id: int | None = None,
) -> Inspection | None:
    """
    Retourne l'inspection PLANIFIEE du même transformateur et du même type située à moins de
    PERIODE_DOUBLON_JOURS jours de `date_inspection` (la plus proche), sinon None.
    """
    marge = timedelta(days=PERIODE_DOUBLON_JOURS - 1)
    stmt = select(Inspection).where(
        Inspection.transformateur_id == transformateur_id,
        Inspection.statut == StatutInspection.PLANIFIEE,
        Inspection.type == type_inspection,
        Inspection.date_inspection >= date_inspection - marge,
        Inspection.date_inspection <= date_inspection + marge,
    )
    if exclure_id is not None:
        stmt = stmt.where(Inspection.id != exclure_id)

    candidates = db.scalars(stmt).all()
    if not candidates:
        return None
    return min(candidates, key=lambda i: (abs((i.date_inspection - date_inspection).days), i.id))
