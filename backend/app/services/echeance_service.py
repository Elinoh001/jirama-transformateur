from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.transformateur import Transformateur
from app.schemas.echeance import EcheanceItem, EcheancesRead
from app.services import preventive_service


def prochaines_inspections(
    db: Session, limit: int = 5, aujourdhui: date | None = None
) -> EcheancesRead:
    """Postes actifs triés par échéance d'inspection (les retards d'abord)."""
    aujourdhui = aujourdhui or date.today()
    base = (Transformateur.actif.is_(True), Transformateur.prochaine_inspection.is_not(None))

    en_retard = (
        db.scalar(
            select(func.count())
            .select_from(Transformateur)
            .where(*base, Transformateur.prochaine_inspection < aujourdhui)
        )
        or 0
    )

    postes = list(
        db.scalars(
            select(Transformateur)
            .where(*base)
            .order_by(Transformateur.prochaine_inspection, Transformateur.reference)
            .limit(limit)
        ).all()
    )
    resultats = preventive_service.evaluer_transformateurs(db, postes)

    items = [
        EcheanceItem(
            transformateur_id=t.id,
            reference=t.reference,
            nom=t.nom,
            secteur=t.secteur,
            prochaine_inspection=t.prochaine_inspection,
            jours_restants=(t.prochaine_inspection - aujourdhui).days,
            periodicite_inspection_mois=t.periodicite_inspection_mois,
            niveau=resultats[t.id].niveau,
        )
        for t in postes
    ]
    return EcheancesRead(en_retard=en_retard, items=items)