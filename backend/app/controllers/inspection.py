from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inspection import Inspection, StatutInspection
from app.models.transformateur import EtatTransformateur
from app.models.utilisateur import Utilisateur
from app.schemas.inspection import InspectionCreate, InspectionRead, InspectionUpdate
from app.services import inspection_service, transformateur_service
from app.services.echeance_inspection import PERIODE_DOUBLON_JOURS
from app.services.inspection_service import PlanificationEnDoublon

# Seul champ qu'on peut compléter après coup sur une inspection réalisée.
CHAMPS_MODIFIABLES_SI_REALISEE = {"observation"}
# Champs que le client peut envoyer à null pour les effacer (les autres null sont ignorés).
CHAMPS_NULLABLES = {"observation", "etat_huile"}


def _erreur(message: str) -> HTTPException:
    return HTTPException(422, message)


def _conflit(message: str) -> HTTPException:
    return HTTPException(status.HTTP_409_CONFLICT, message)


def _doublon(e: PlanificationEnDoublon) -> HTTPException:
    x = e.existante
    return _conflit(
        f"Une inspection {x.type} est déjà planifiée le {x.date_inspection.strftime('%d/%m/%Y')} "
        f"(n° {x.id}) pour ce transformateur, à moins de {PERIODE_DOUBLON_JOURS} jours. "
        "Reportez-la ou annulez-la avant d'en planifier une autre."
    )


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


def _champs_modifies(inspection: Inspection, champs: dict) -> set[str]:
    """
    Champs dont la valeur envoyée DIFFÈRE de la valeur enregistrée. Les formulaires renvoient tous
    les champs, même inchangés : seules les vraies modifications doivent être contrôlées.
    """
    modifies = set()
    for champ, valeur in champs.items():
        if valeur is None and champ not in CHAMPS_NULLABLES:
            continue
        if valeur != getattr(inspection, champ):
            modifies.add(champ)
    return modifies


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
    try:
        return to_read(inspection_service.create_inspection(db, data, technicien))
    except PlanificationEnDoublon as e:
        db.rollback()
        raise _doublon(e)


def update_inspection(db: Session, inspection_id: int, data: InspectionUpdate) -> InspectionRead:
    inspection = _get_or_404(db, inspection_id)
    champs = data.model_dump(exclude_unset=True)

    # --- Inspection annulée : archivée, définitive ---
    if inspection.statut == StatutInspection.ANNULEE:
        raise _conflit(
            "Une inspection annulée est archivée et ne peut plus être modifiée. "
            "Planifiez une nouvelle inspection si nécessaire."
        )

    # --- Inspection réalisée : figée pour conserver l'historique du carnet d'entretien ---
    if inspection.statut == StatutInspection.REALISEE:
        interdits = _champs_modifies(inspection, champs) - CHAMPS_MODIFIABLES_SI_REALISEE
        if interdits:
            raise _conflit(
                "Une inspection réalisée est figée pour conserver l'historique : elle ne peut être ni "
                "annulée, ni replanifiée, ni modifiée (champs refusés : "
                f"{', '.join(sorted(interdits))}). Seule l'observation peut être complétée."
            )
        return to_read(inspection_service.update_inspection(db, inspection, data))

    # --- Inspection planifiée ---
    statut = data.statut or inspection.statut

    if statut == StatutInspection.ANNULEE:
        pass  # annulation : toujours possible, l'échéance est recalculée par le service

    elif statut == StatutInspection.REALISEE:
        etat = data.etat or inspection.etat
        date_finale = data.date_inspection or inspection.date_inspection
        if etat is None:
            raise _erreur("L'état constaté est obligatoire pour une inspection réalisée")
        if date_finale > date.today():
            raise _erreur(
                "La date d'une inspection réalisée ne peut pas être dans le futur : "
                "indiquez la date réelle de l'inspection"
            )

    else:  # reste PLANIFIEE : report ou simple correction
        if data.etat is not None or data.etat_huile is not None:
            raise _erreur("L'état constaté et l'état de l'huile se saisissent à la réalisation de l'inspection")
        if data.date_inspection is not None and data.date_inspection < date.today():
            raise _erreur("Impossible de planifier une inspection à une date passée")

    try:
        return to_read(inspection_service.update_inspection(db, inspection, data))
    except PlanificationEnDoublon as e:
        db.rollback()
        raise _doublon(e)
