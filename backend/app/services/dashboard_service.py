from collections import Counter
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inspection import Inspection
from app.models.intervention import Intervention, StatutIntervention
from app.models.transformateur import EtatTransformateur, Transformateur
from app.schemas.dashboard import ActiviteMois, DashboardStatistics, RepartitionPriorites
from app.services import preventive_service, transformateur_service
from app.services.preventive_service import NiveauPriorite

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
    resultats = preventive_service.evaluer_transformateurs(db, transformateurs_actifs)
    niveaux = Counter(r.niveau for r in resultats.values())

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
        activite_mensuelle=_activite_mensuelle(db, aujourdhui),
        cout_total_interventions_terminees=float(cout_total or 0),
    )