from collections import Counter
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.intervention import Intervention, StatutIntervention
from app.config.referentiels import SECTEURS_ANTSIRABE
from app.models.panne import GravitePanne, Panne, StatutPanne
from app.models.transformateur import EtatTransformateur, Transformateur
from app.schemas.dashboard import (
    ActiviteMois,
    DashboardStatistics,
    RepartitionPriorites,
    RepartitionStatuts,
    SecteurStat,
)
from app.services import preventive_service, spatial_service, statut_service, transformateur_service
from app.services.preventive_service import NiveauPriorite
from app.services.statut_service import SEUIL_SURCHARGE_POURCENT, StatutOperationnel

NB_MOIS_ACTIVITE = 6


def _derniers_mois(aujourdhui: date, nombre: int) -> list[tuple[int, int]]:
    """Retourne les `nombre` derniers mois (année, mois), du plus ancien au mois courant."""
    annee, mois = aujourdhui.year, aujourdhui.month
    resultat: list[tuple[int, int]] = []
    for _ in range(nombre):
        resultat.append((annee, mois))
        mois -= 1
        if mois == 0:
            mois = 12
            annee -= 1
    return list(reversed(resultat))


def _compter(db: Session, stmt) -> int:
    return db.scalar(stmt) or 0


def _activite_mensuelle(db: Session, aujourdhui: date) -> list[ActiviteMois]:
    mois_list = _derniers_mois(aujourdhui, NB_MOIS_ACTIVITE)
    debut = date(mois_list[0][0], mois_list[0][1], 1)

    dates_inspections = db.scalars(
        select(Inspection.date_inspection).where(Inspection.date_inspection >= debut)
    ).all()
    dates_interventions = db.scalars(
        select(Intervention.date_intervention).where(Intervention.date_intervention >= debut)
    ).all()

    par_mois_insp = Counter((d.year, d.month) for d in dates_inspections)
    par_mois_interv = Counter((d.year, d.month) for d in dates_interventions)

    return [
        ActiviteMois(
            mois=f"{annee}-{mois:02d}",
            inspections=par_mois_insp.get((annee, mois), 0),
            interventions=par_mois_interv.get((annee, mois), 0),
        )
        for annee, mois in mois_list
    ]


def _synthese_secteurs(
    db: Session, postes: list[Transformateur], situations: dict
) -> list[SecteurStat]:
    """Une ligne par secteur contenant au moins un poste actif (ordre du référentiel)."""
    centres = spatial_service.centres_secteurs(db, actif=True)
    par_secteur: dict[str, list[Transformateur]] = {}
    for t in postes:
        par_secteur.setdefault(t.secteur, []).append(t)

    ordre = [s for s in SECTEURS_ANTSIRABE if s in par_secteur]
    ordre += sorted(s for s in par_secteur if s not in SECTEURS_ANTSIRABE)

    lignes: list[SecteurStat] = []
    for secteur in ordre:
        membres = par_secteur[secteur]
        centre = centres.get(secteur)
        lignes.append(
            SecteurStat(
                secteur=secteur,
                total=len(membres),
                en_surcharge=sum(
                    1
                    for t in membres
                    if (situations[t.id].taux_charge or 0) > SEUIL_SURCHARGE_POURCENT
                ),
                en_panne=sum(1 for t in membres if situations[t.id].statut == StatutOperationnel.EN_PANNE),
                pannes_actives=sum(situations[t.id].nb_pannes_actives for t in membres),
                latitude_centre=centre[0] if centre else None,
                longitude_centre=centre[1] if centre else None,
            )
        )
    return lignes


def get_statistics(db: Session) -> DashboardStatistics:
    aujourdhui = date.today()

    # --- Transformateurs ---
    total = _compter(db, select(func.count()).select_from(Transformateur))
    actifs = _compter(
        db, select(func.count()).select_from(Transformateur).where(Transformateur.actif.is_(True))
    )
    par_etat = dict(
        db.execute(select(Transformateur.etat, func.count()).group_by(Transformateur.etat)).all()
    )

    # --- Inspections et interventions ---
    total_inspections = _compter(db, select(func.count()).select_from(Inspection))
    total_interventions = _compter(db, select(func.count()).select_from(Intervention))
    par_statut = dict(
        db.execute(
            select(Intervention.statut, func.count()).group_by(Intervention.statut)
        ).all()
    )
    cout_total = db.scalar(
        select(func.coalesce(func.sum(Intervention.cout), 0)).where(
            Intervention.statut == StatutIntervention.TERMINEE
        )
    )

    # --- Suivi préventif : uniquement les transformateurs actifs ---
    transformateurs_actifs = transformateur_service.list_transformateurs(
        db, actif=True, limit=1000
    )
    situations = statut_service.evaluer_postes(db, [t.id for t in transformateurs_actifs])
    resultats = preventive_service.evaluer_transformateurs(db, transformateurs_actifs, situations)
    niveaux = Counter(r.niveau for r in resultats.values())

    # --- Statut opérationnel, charge et pannes ---
    statuts = Counter(sit.statut for sit in situations.values())
    taux = [sit.taux_charge for sit in situations.values() if sit.taux_charge is not None]
    pannes_actives = _compter(
        db, select(func.count()).select_from(Panne).where(Panne.statut != StatutPanne.RESOLUE)
    )
    pannes_critiques = _compter(
        db,
        select(func.count())
        .select_from(Panne)
        .where(Panne.statut != StatutPanne.RESOLUE, Panne.gravite == GravitePanne.CRITIQUE),
    )

    return DashboardStatistics(
        total_transformateurs=total,
        transformateurs_actifs=actifs,
        transformateurs_inactifs=total - actifs,
        transformateurs_bon=par_etat.get(EtatTransformateur.BON, 0),
        transformateurs_a_surveiller=par_etat.get(EtatTransformateur.A_SURVEILLER, 0),
        transformateurs_critiques=par_etat.get(EtatTransformateur.CRITIQUE, 0),
        total_inspections=total_inspections,
        total_interventions=total_interventions,
        interventions_planifiees=par_statut.get(StatutIntervention.PLANIFIEE, 0),
        interventions_en_cours=par_statut.get(StatutIntervention.EN_COURS, 0),
        interventions_terminees=par_statut.get(StatutIntervention.TERMINEE, 0),
        interventions_annulees=par_statut.get(StatutIntervention.ANNULEE, 0),
        nb_priorites=niveaux.get(NiveauPriorite.PRIORITAIRE, 0),
        repartition_priorites=RepartitionPriorites(
            normal=niveaux.get(NiveauPriorite.NORMAL, 0),
            a_surveiller=niveaux.get(NiveauPriorite.A_SURVEILLER, 0),
            prioritaire=niveaux.get(NiveauPriorite.PRIORITAIRE, 0),
        ),
        repartition_statuts=RepartitionStatuts(
            en_service=statuts.get(StatutOperationnel.EN_SERVICE, 0),
            en_surcharge=statuts.get(StatutOperationnel.EN_SURCHARGE, 0),
            en_maintenance=statuts.get(StatutOperationnel.EN_MAINTENANCE, 0),
            en_panne=statuts.get(StatutOperationnel.EN_PANNE, 0),
        ),
        taux_charge_moyen=round(sum(taux) / len(taux), 2) if taux else None,
        postes_en_surcharge=sum(1 for x in taux if x > SEUIL_SURCHARGE_POURCENT),
        pannes_actives=pannes_actives,
        pannes_critiques_actives=pannes_critiques,
        repartition_secteurs=_synthese_secteurs(db, transformateurs_actifs, situations),
        activite_mensuelle=_activite_mensuelle(db, aujourdhui),
        cout_total_interventions_terminees=float(cout_total or 0),
    )