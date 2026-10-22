from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inspection import Inspection, StatutInspection
from app.models.transformateur import EtatTransformateur
from app.models.utilisateur import Utilisateur
from app.schemas.inspection import InspectionCreate, InspectionRead, InspectionUpdate
from app.services import inspection_service, transformateur_service


def _erreur(message: str) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, message)


def to_read(i: Inspection) -> InspectionRead:
    return InspectionRead(
        id=i.id,
        transformateur_id=i.transformateur_id,
        transformateur_reference=i.transformateur.reference,
        transformateur_nom=i.transformateur.nom,
        date_inspection=i.date_inspection,
        type=i.type,
        statut=i.statut,
        etat=i.etat,
        etat_huile=i.etat_huile,
        observation=i.observation,
        technicien=i.technicien,
        created_at=i.created_at,
    )


def _get_or_404(db: Session, inspection_id: int) -> Inspection:
    inspection = inspection_service.get_by_id(db, inspection_id)
    if inspection is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Inspection introuvable")
    return inspection


def list_inspections(
    db: Session,
    transformateur_id: int | None,
    etat: EtatTransformateur | None,
    statut: StatutInspection | None,
    skip: int,
    limit: int,
) -> list[InspectionRead]:
    items = inspection_service.list_inspections(db, transformateur_id, etat, statut, skip, limit)
    return [to_read(i) for i in items]


def get_inspection(db: Session, inspection_id: int) -> InspectionRead:
    return to_read(_get_or_404(db, inspection_id))


def create_inspection(
    db: Session, data: InspectionCreate, current_user: Utilisateur
) -> InspectionRead:
    if transformateur_service.get_by_id(db, data.transformateur_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transformateur introuvable")

    technicien = data.technicien or f"{current_user.prenom} {current_user.nom}"
    return to_read(inspection_service.create_inspection(db, data, technicien))


def update_inspection(db: Session, inspection_id: int, data: InspectionUpdate) -> InspectionRead:
    inspection = _get_or_404(db, inspection_id)

    # Valeurs finales après modification (un champ absent ou null conserve la valeur actuelle).
    statut = data.statut or inspection.statut
    etat = data.etat or inspection.etat
    date_finale = data.date_inspection or inspection.date_inspection

    if statut == StatutInspection.REALISEE:
        if etat is None:
            raise _erreur("L'état constaté est obligatoire pour une inspection réalisée")
        if date_finale > date.today():
            raise _erreur("La date d'une inspection réalisée ne peut pas être dans le futur")
    elif statut == StatutInspection.PLANIFIEE:
        if inspection.statut == StatutInspection.REALISEE:
            raise _erreur("Une inspection réalisée ne peut pas redevenir planifiée")
        if data.date_inspection is not None and data.date_inspection < date.today():
            raise _erreur("Impossible de planifier une inspection à une date passée")

    return to_read(inspection_service.update_inspection(db, inspection, data))