from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.intervention import Intervention, StatutIntervention
from app.models.utilisateur import Utilisateur
from app.schemas.intervention import InterventionCreate, InterventionRead, InterventionUpdate
from app.services import intervention_service, transformateur_service


def to_read(i: Intervention) -> InterventionRead:
    return InterventionRead(
        id=i.id,
        transformateur_id=i.transformateur_id,
        transformateur_reference=i.transformateur.reference,
        transformateur_nom=i.transformateur.nom,
        date_intervention=i.date_intervention,
        type=i.type,
        description=i.description,
        cout=float(i.cout) if i.cout is not None else None,
        statut=i.statut,
        technicien=i.technicien,
        created_at=i.created_at,
    )


def _get_or_404(db: Session, intervention_id: int) -> Intervention:
    intervention = intervention_service.get_by_id(db, intervention_id)
    if intervention is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Intervention introuvable")
    return intervention


def list_interventions(
    db: Session,
    transformateur_id: int | None,
    statut: StatutIntervention | None,
    skip: int,
    limit: int,
) -> list[InterventionRead]:
    items = intervention_service.list_interventions(db, transformateur_id, statut, skip, limit)
    return [to_read(i) for i in items]


def get_intervention(db: Session, intervention_id: int) -> InterventionRead:
    return to_read(_get_or_404(db, intervention_id))


def create_intervention(
    db: Session, data: InterventionCreate, current_user: Utilisateur
) -> InterventionRead:
    if transformateur_service.get_by_id(db, data.transformateur_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transformateur introuvable")

    technicien = data.technicien or f"{current_user.prenom} {current_user.nom}"
    return to_read(intervention_service.create_intervention(db, data, technicien))


def update_intervention(
    db: Session, intervention_id: int, data: InterventionUpdate
) -> InterventionRead:
    intervention = _get_or_404(db, intervention_id)
    return to_read(intervention_service.update_intervention(db, intervention, data))