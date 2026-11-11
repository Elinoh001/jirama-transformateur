"""
Suivi préventif : calcul de la priorité d'un transformateur par règles simples.
Aucune IA : uniquement des conditions explicites (état, inspections, pannes, charge, huile).

Niveaux : NORMAL < A_SURVEILLER < PRIORITAIRE

Règles PRIORITAIRE : état CRITIQUE, dernière inspection CRITIQUE, 2 inspections CRITIQUE récentes,
panne CRITIQUE active, surcharge (> 100 %), niveau d'huile CRITIQUE, inspection en retard de
plus de 30 jours.
Règles A_SURVEILLER : état A_SURVEILLER, dernière inspection A_SURVEILLER, aucune inspection ou
inspection ancienne, autre panne active, charge élevée (>= 80 %), niveau d'huile BAS, inspection
en retard (30 jours ou moins).

Le retard d'inspection est défini dans services/echeance_inspection.py (échéance théorique
dépassée, ou inspection planifiée non réalisée après sa date).

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
from app.models.transformateur import EtatTransformateur, NiveauHuile, Transformateur
from app.services import echeance_inspection, statut_service
from app.services.echeance_inspection import SituationEcheance
from app.services.statut_service import SEUIL_SURCHARGE_POURCENT, SituationPoste

# --- Seuils des règles (modifiables) ---
SEUIL_INSPECTION_ANCIENNE_JOURS = 365  # au-delà : inspection considérée comme ancienne
FENETRE_ANOMALIES_JOURS = 180  # période observée pour compter les anomalies
NB_ANOMALIES_PRIORITAIRE = 2  # nb d'inspections CRITIQUE (dans la fenêtre) => PRIORITAIRE
SEUIL_CHARGE_ELEVEE_POURCENT = 80.0  # charge élevée mais encore sous la puissance nominale
SEUIL_RETARD_PRIORITAIRE_JOURS = 30  # inspection en retard de plus de N jours => PRIORITAIRE


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
    # Échéances d'inspection (renseignées par evaluer_transformateurs)
    echeance_theorique: date | None = None
    prochaine_planifiee: date | None = None
    jours_retard_inspection: int = 0


def calculer_priorite(
    etat: EtatTransformateur,
    inspections: Iterable[InspectionLike],
    aujourdhui: date | None = None,
    *,
    nb_pannes_critiques: int = 0,
    nb_pannes_actives: int = 0,
    taux_charge: float | None = None,
    niveau_huile: NiveauHuile | None = None,
    jours_retard_inspection: int = 0,
) -> ResultatPriorite:
    """
    Fonction pure : ne dépend pas de la base de données.
    Retourne le niveau de priorité et la liste des motifs qui l'expliquent.
    Les paramètres nommés (pannes, charge, huile) sont facultatifs.
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

    if nb_pannes_critiques > 0:
        motifs_prioritaire.append(f"{nb_pannes_critiques} panne(s) critique(s) active(s)")
    if taux_charge is not None and taux_charge > SEUIL_SURCHARGE_POURCENT:
        motifs_prioritaire.append(f"Surcharge : {taux_charge:.1f} % de la puissance nominale")
    if niveau_huile == NiveauHuile.CRITIQUE:
        motifs_prioritaire.append("Niveau d'huile CRITIQUE")
    if jours_retard_inspection > SEUIL_RETARD_PRIORITAIRE_JOURS:
        motifs_prioritaire.append(
            f"Inspection en retard de {jours_retard_inspection} jours (seuil : {SEUIL_RETARD_PRIORITAIRE_JOURS})"
        )

    # --- Règles A_SURVEILLER ---
    if nb_pannes_actives - nb_pannes_critiques > 0:
        motifs_surveiller.append(f"{nb_pannes_actives - nb_pannes_critiques} autre(s) panne(s) active(s)")
    if taux_charge is not None and SEUIL_CHARGE_ELEVEE_POURCENT <= taux_charge <= SEUIL_SURCHARGE_POURCENT:
        motifs_surveiller.append(f"Charge élevée : {taux_charge:.1f} %")
    if niveau_huile == NiveauHuile.BAS:
        motifs_surveiller.append("Niveau d'huile bas")
    if 0 < jours_retard_inspection <= SEUIL_RETARD_PRIORITAIRE_JOURS:
        motifs_surveiller.append(f"Inspection en retard de {jours_retard_inspection} jour(s)")
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
        jours_retard_inspection=jours_retard_inspection,
    )


def evaluer_transformateurs(
    db: Session,
    transformateurs: list[Transformateur],
    situations: dict[int, SituationPoste] | None = None,
    echeances: dict[int, SituationEcheance] | None = None,
) -> dict[int, ResultatPriorite]:
    """
    Calcule la priorité de plusieurs transformateurs (requêtes groupées, pas une par poste).
    `situations` (pannes, charge) et `echeances` (retard d'inspection) peuvent être fournis
    pour éviter de les recalculer.
    """
    if not transformateurs:
        return {}

    ids = [t.id for t in transformateurs]
    if situations is None:
        situations = statut_service.evaluer_postes(db, ids)
    if echeances is None:
        echeances = echeance_inspection.evaluer_echeances(db, transformateurs)

    inspections = db.scalars(
        select(Inspection).where(
            Inspection.transformateur_id.in_(ids),
            Inspection.statut == StatutInspection.REALISEE,
        )
    ).all()

    par_transformateur: dict[int, list[Inspection]] = defaultdict(list)
    for inspection in inspections:
        par_transformateur[inspection.transformateur_id].append(inspection)

    resultats: dict[int, ResultatPriorite] = {}
    for t in transformateurs:
        echeance = echeances[t.id]
        resultat = calculer_priorite(
            t.etat,
            par_transformateur[t.id],
            nb_pannes_critiques=situations[t.id].nb_pannes_critiques_actives,
            nb_pannes_actives=situations[t.id].nb_pannes_actives,
            taux_charge=situations[t.id].taux_charge,
            niveau_huile=t.niveau_huile,
            jours_retard_inspection=echeance.jours_retard,
        )
        resultat.echeance_theorique = echeance.echeance_theorique
        resultat.prochaine_planifiee = echeance.prochaine_planifiee
        resultats[t.id] = resultat
    return resultats


def evaluer_transformateur(db: Session, transformateur: Transformateur) -> ResultatPriorite:
    return evaluer_transformateurs(db, [transformateur])[transformateur.id]
