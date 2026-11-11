from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transformateur import Transformateur
from app.schemas.echeance import EcheanceItem, EcheancesRead
from app.services import echeance_inspection, preventive_service


def prochaines_inspections(
    db: Session, limit: int = 5, aujourdhui: date | None = None
) -> EcheancesRead:
    """
    Postes actifs triés par échéance : les postes en retard d'abord (le plus en retard en premier),
    puis par date de prochaine inspection prévue.
    """
    aujourdhui = aujourdhui or date.today()
    postes = list(
        db.scalars(select(Transformateur).where(Transformateur.actif.is_(True))).all()
    )
    echeances = echeance_inspection.evaluer_echeances(db, postes, aujourdhui)

    def cle_tri(t: Transformateur):
        e = echeances[t.id]
        return (0 if e.en_retard else 1, -e.jours_retard, e.prochaine_prevue, t.reference)

    tries = sorted(postes, key=cle_tri)
    en_retard = sum(1 for e in echeances.values() if e.en_retard)

    retenus = tries[:limit]
    resultats = preventive_service.evaluer_transformateurs(db, retenus, echeances=echeances)

    items = [
        EcheanceItem(
            transformateur_id=t.id,
            reference=t.reference,
            nom=t.nom,
            secteur=t.secteur,
            prochaine_inspection=echeances[t.id].prochaine_prevue,
            jours_restants=(
                -echeances[t.id].jours_retard
                if echeances[t.id].en_retard
                else (echeances[t.id].prochaine_prevue - aujourdhui).days
            ),
            periodicite_inspection_mois=t.periodicite_inspection_mois,
            niveau=resultats[t.id].niveau,
            echeance_theorique=echeances[t.id].echeance_theorique,
            source=echeances[t.id].source,
            en_retard=echeances[t.id].en_retard,
            jours_retard=echeances[t.id].jours_retard,
        )
        for t in retenus
    ]
    return EcheancesRead(en_retard=en_retard, items=items)
