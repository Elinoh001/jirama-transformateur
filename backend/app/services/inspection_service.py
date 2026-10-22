from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.inspection import Inspection, StatutInspection
from app.models.transformateur import EtatTransformateur, Transformateur
from app.schemas.inspection import InspectionCreate, InspectionUpdate
from app.services import transformateur_service

# Champs que l'on peut remettre à null explicitement.
CHAMPS_NULLABLES = {"observation", "etat_huile"}


def get_by_id(db: Session, inspection_id: int) -> Inspection | None:
    return db.get(Inspection, inspection_id)


def list_inspections(
    db: Session,
    transformateur_id: int | None = None,
    etat: EtatTransformateur | None = None,
    statut: StatutInspection | None = None,
    skip: int = 0,
    limit: int = 500,
) -> list[Inspection]:
    stmt = (
        select(Inspection)
        .options(joinedload(Inspection.transformateur))
        .order_by(Inspection.date_inspection.desc(), Inspection.id.desc())
    )
    if transformateur_id is not None:
        stmt = stmt.where(Inspection.transformateur_id == transformateur_id)
    if etat is not None:
        stmt = stmt.where(Inspection.etat == etat)
    if statut is not None:
        stmt = stmt.where(Inspection.statut == statut)

    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def _maj_echeance(db: Session, transformateur_id: int) -> None:
    """Recalcule la prochaine inspection du transformateur (sans commit)."""
    transformateur = db.get(Transformateur, transformateur_id)
    if transformateur is not None:
        transformateur_service.recalculer_prochaine_inspection(db, transformateur)


def create_inspection(db: Session, data: InspectionCreate, technicien: str) -> Inspection:
    inspection = Inspection(
        transformateur_id=data.transformateur_id,
        date_inspection=data.date_inspection,
        type=data.type,
        statut=data.statut,
        etat=data.etat,
        etat_huile=data.etat_huile,
        observation=data.observation,
        technicien=technicien,
    )
    db.add(inspection)
    db.flush()  # autoflush désactivé : nécessaire avant le recalcul de l'échéance
    _maj_echeance(db, data.transformateur_id)
    db.commit()
    db.refresh(inspection)
    return inspection


def update_inspection(db: Session, inspection: Inspection, data: InspectionUpdate) -> Inspection:
    values = data.model_dump(exclude_unset=True)

    for champ, valeur in values.items():
        if valeur is None and champ not in CHAMPS_NULLABLES:
            continue
        setattr(inspection, champ, valeur)

    db.flush()
    _maj_echeance(db, inspection.transformateur_id)
    db.commit()
    db.refresh(inspection)
    return inspection