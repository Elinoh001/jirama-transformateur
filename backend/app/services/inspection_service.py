from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.inspection import Inspection, StatutInspection
from app.models.transformateur import EtatTransformateur, Transformateur
from app.schemas.inspection import InspectionCreate, InspectionUpdate
from app.services import echeance_inspection

# Champs que l'on peut remettre à null explicitement.
CHAMPS_NULLABLES = {"observation", "etat_huile"}


class PlanificationEnDoublon(Exception):
    """Une inspection du même type est déjà planifiée sur la même période pour ce transformateur."""

    def __init__(self, existante: Inspection) -> None:
        super().__init__("planification en doublon")
        self.existante = existante


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
    """Recalcule la prochaine inspection prévue du transformateur (sans commit)."""
    transformateur = db.get(Transformateur, transformateur_id)
    if transformateur is not None:
        echeance_inspection.synchroniser_prochaine_inspection(db, transformateur)


def create_inspection(db: Session, data: InspectionCreate, technicien: str) -> Inspection:
    """
    - PLANIFIEE : refusée (PlanificationEnDoublon) si une inspection planifiée du même type existe
      déjà à moins de 30 jours pour ce transformateur.
    - REALISEE : si une inspection planifiée du même type existe sur la même période, c'est elle qui
      est clôturée (même ligne, statut REALISEE) : pas de planification fantôme qui passerait en retard.
    """
    # Verrou de ligne : les créations simultanées pour un même transformateur passent l'une après l'autre.
    echeance_inspection.verrouiller_transformateur(db, data.transformateur_id)
    proche = echeance_inspection.trouver_planification_proche(
        db, data.transformateur_id, data.type, data.date_inspection
    )

    if data.statut == StatutInspection.PLANIFIEE and proche is not None:
        raise PlanificationEnDoublon(proche)

    if data.statut == StatutInspection.REALISEE and proche is not None:
        inspection = proche  # clôture de la planification existante
        inspection.date_inspection = data.date_inspection
        inspection.statut = StatutInspection.REALISEE
        inspection.etat = data.etat
        inspection.etat_huile = data.etat_huile
        inspection.observation = data.observation or inspection.observation
        inspection.technicien = technicien
    else:
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
    """Applique la modification. Les règles métier sont vérifiées au préalable par le contrôleur."""
    values = data.model_dump(exclude_unset=True)
    statut_final = values.get("statut") or inspection.statut

    if statut_final == StatutInspection.ANNULEE:
        # Une annulation ne modifie que le statut (et éventuellement le motif en observation).
        values = {k: v for k, v in values.items() if k in {"statut", "observation"}}

    elif statut_final == StatutInspection.PLANIFIEE and (
        values.get("date_inspection") is not None or values.get("type") is not None
    ):
        # Report ou changement de type : on vérifie qu'on ne crée pas un doublon de planification.
        echeance_inspection.verrouiller_transformateur(db, inspection.transformateur_id)
        doublon = echeance_inspection.trouver_planification_proche(
            db,
            inspection.transformateur_id,
            values.get("type") or inspection.type,
            values.get("date_inspection") or inspection.date_inspection,
            exclure_id=inspection.id,
        )
        if doublon is not None:
            raise PlanificationEnDoublon(doublon)

    for champ, valeur in values.items():
        if valeur is None and champ not in CHAMPS_NULLABLES:
            continue
        setattr(inspection, champ, valeur)

    db.flush()
    _maj_echeance(db, inspection.transformateur_id)  # annulation, report ou réalisation : échéance à jour
    db.commit()
    db.refresh(inspection)
    return inspection
