"""
Statut OPÉRATIONNEL d'un transformateur : calculé à la demande, jamais stocké en base.

Trois notions à ne pas confondre :
  - l'ÉTAT TECHNIQUE du poste (BON / A_SURVEILLER / CRITIQUE) : colonne `etat`, saisie à l'inspection ;
  - le STATUT D'UNE PANNE (SIGNALEE / EN_COURS / RESOLUE) et sa GRAVITÉ (MINEURE / MAJEURE / CRITIQUE) ;
  - le TAUX DE CHARGE issu du dernier relevé.
Le statut opérationnel résume ces informations en un seul état affiché sur la carte et la fiche.

Comme il est recalculé à chaque lecture, il ne peut jamais être en désaccord avec les pannes :
  - règle 4 : une panne CRITIQUE active met le poste « en panne » ;
  - règle 7 : toute panne active (quelle que soit sa gravité) ou toute intervention en cours
    empêche le retour à « en service ».

Priorité des règles (la première qui correspond l'emporte) :
  1. EN_PANNE        : au moins une panne CRITIQUE active
  2. EN_MAINTENANCE  : au moins une autre panne active (MINEURE / MAJEURE) ou une intervention EN_COURS
  3. EN_SURCHARGE    : dernier taux de charge > 100 %
  4. EN_SERVICE      : aucun des cas précédents
"""
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.intervention import Intervention, StatutIntervention
from app.models.panne import GravitePanne, Panne, StatutPanne
from app.models.releve_charge import ReleveCharge

SEUIL_SURCHARGE_POURCENT = 100.0


class StatutOperationnel(str, Enum):
    EN_SERVICE = "EN_SERVICE"
    EN_SURCHARGE = "EN_SURCHARGE"
    EN_MAINTENANCE = "EN_MAINTENANCE"
    EN_PANNE = "EN_PANNE"


@dataclass
class SituationPoste:
    statut: StatutOperationnel
    nb_pannes_actives: int
    nb_pannes_critiques_actives: int
    nb_interventions_en_cours: int
    taux_charge: float | None


def calculer_statut(
    nb_pannes_critiques_actives: int,
    nb_pannes_actives: int,
    nb_interventions_en_cours: int,
    taux_charge: float | None,
) -> StatutOperationnel:
    """Fonction pure (sans base de données) : facile à tester et à expliquer."""
    if nb_pannes_critiques_actives > 0:
        return StatutOperationnel.EN_PANNE
    if nb_pannes_actives > 0 or nb_interventions_en_cours > 0:
        return StatutOperationnel.EN_MAINTENANCE
    if taux_charge is not None and taux_charge > SEUIL_SURCHARGE_POURCENT:
        return StatutOperationnel.EN_SURCHARGE
    return StatutOperationnel.EN_SERVICE


def evaluer_postes(db: Session, ids: list[int]) -> dict[int, SituationPoste]:
    """Calcule la situation de plusieurs transformateurs avec 3 requêtes SQL au total."""
    if not ids:
        return {}

    # 1) pannes actives (statut différent de RESOLUE), par transformateur et gravité
    lignes_pannes = db.execute(
        select(Panne.transformateur_id, Panne.gravite, func.count())
        .where(Panne.transformateur_id.in_(ids), Panne.statut != StatutPanne.RESOLUE)
        .group_by(Panne.transformateur_id, Panne.gravite)
    ).all()
    actives: dict[int, int] = defaultdict(int)
    critiques: dict[int, int] = defaultdict(int)
    for transformateur_id, gravite, nombre in lignes_pannes:
        actives[transformateur_id] += nombre
        if gravite == GravitePanne.CRITIQUE:
            critiques[transformateur_id] += nombre

    # 2) interventions en cours
    en_cours = dict(
        db.execute(
            select(Intervention.transformateur_id, func.count())
            .where(
                Intervention.transformateur_id.in_(ids),
                Intervention.statut == StatutIntervention.EN_COURS,
            )
            .group_by(Intervention.transformateur_id)
        ).all()
    )

    # 3) dernier relevé de charge de chaque transformateur (DISTINCT ON, propre à PostgreSQL)
    derniers = db.scalars(
        select(ReleveCharge)
        .where(ReleveCharge.transformateur_id.in_(ids))
        .order_by(
            ReleveCharge.transformateur_id,
            ReleveCharge.date_releve.desc(),
            ReleveCharge.id.desc(),
        )
        .distinct(ReleveCharge.transformateur_id)
    ).all()
    taux = {r.transformateur_id: r.taux_charge for r in derniers}

    resultat: dict[int, SituationPoste] = {}
    for i in ids:
        resultat[i] = SituationPoste(
            statut=calculer_statut(critiques[i], actives[i], en_cours.get(i, 0), taux.get(i)),
            nb_pannes_actives=actives[i],
            nb_pannes_critiques_actives=critiques[i],
            nb_interventions_en_cours=en_cours.get(i, 0),
            taux_charge=taux.get(i),
        )
    return resultat


def evaluer_poste(db: Session, transformateur_id: int) -> SituationPoste:
    return evaluer_postes(db, [transformateur_id])[transformateur_id]
