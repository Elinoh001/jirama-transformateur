from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.intervention import Intervention, StatutIntervention
from app.schemas.intervention import InterventionCreate, InterventionUpdate

# Champs que l'on peut remettre à null explicitement.
CHAMPS_NULLABLES = {"description", "cout"}


def get_by_id(db: Session, intervention_id: int) -> Intervention | None:
    return db.get(Intervention, intervention_id)


def list_interventions(
    db: Session,
    transformateur_id: int | None = None,
    statut: StatutIntervention | None = None,
    skip: int = 0,
    limit: int = 500,
) -> list[Intervention]:
    stmt = (
        select(Intervention)
        .options(joinedload(Intervention.transformateur))
        .order_by(Intervention.date_intervention.desc(), Intervention.id.desc())
    )
    if transformateur_id is not None:
        stmt = stmt.where(Intervention.transformateur_id == transformateur_id)
    if statut is not None:
        stmt = stmt.where(Intervention.statut == statut)

    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_intervention(db: Session, data: InterventionCreate, technicien: str) -> Intervention:
    intervention = Intervention(
        transformateur_id=data.transformateur_id,
        date_intervention=data.date_intervention,
        type=data.type,
        description=data.description,
        cout=data.cout,
        statut=data.statut,
        technicien=technicien,
    )
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention


def update_intervention(
    db: Session, intervention: Intervention, data: InterventionUpdate
) -> Intervention:
    values = data.model_dump(exclude_unset=True)

    for champ, valeur in values.items():
        if valeur is None and champ not in CHAMPS_NULLABLES:
            continue
        setattr(intervention, champ, valeur)

    db.commit()
    db.refresh(intervention)
    return intervention
