from datetime import date

from geoalchemy2.elements import WKTElement
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.inspection import Inspection, StatutInspection
from app.models.transformateur import EtatTransformateur, Transformateur
from app.schemas.transformateur import TransformateurCreate, TransformateurUpdate
from app.utils.dates import ajouter_mois

SRID_WGS84 = 4326

# Champs que l'on peut remettre à null explicitement.
CHAMPS_NULLABLES = {"date_installation", "type_huile"}


def build_point(latitude: float, longitude: float) -> WKTElement:
    """Construit un POINT PostGIS. Attention : WKT = POINT(longitude latitude)."""
    return WKTElement(f"POINT({longitude:.7f} {latitude:.7f})", srid=SRID_WGS84)


def recalculer_prochaine_inspection(db: Session, transformateur: Transformateur) -> None:
    """
    prochaine échéance = dernière inspection RÉALISÉE + périodicité (en mois).
    Sans inspection réalisée : aujourd'hui + périodicité.
    Ne fait pas de commit : c'est à l'appelant de le faire.
    """
    derniere = db.scalar(
        select(func.max(Inspection.date_inspection)).where(
            Inspection.transformateur_id == transformateur.id,
            Inspection.statut == StatutInspection.REALISEE,
        )
    )
    base = derniere or date.today()
    transformateur.prochaine_inspection = ajouter_mois(base, transformateur.periodicite_inspection_mois)


def get_by_id(db: Session, transformateur_id: int) -> Transformateur | None:
    return db.get(Transformateur, transformateur_id)


def get_by_reference(db: Session, reference: str) -> Transformateur | None:
    return db.scalar(select(Transformateur).where(Transformateur.reference == reference))


def list_transformateurs(
    db: Session,
    search: str | None = None,
    etat: EtatTransformateur | None = None,
    actif: bool | None = None,
    skip: int = 0,
    limit: int = 500,
) -> list[Transformateur]:
    stmt = select(Transformateur).order_by(Transformateur.reference)

    if search and search.strip():
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Transformateur.reference.ilike(pattern),
                Transformateur.nom.ilike(pattern),
                Transformateur.secteur.ilike(pattern),
            )
        )
    if etat is not None:
        stmt = stmt.where(Transformateur.etat == etat)
    if actif is not None:
        stmt = stmt.where(Transformateur.actif == actif)

    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_transformateur(db: Session, data: TransformateurCreate) -> Transformateur:
    transformateur = Transformateur(
        reference=data.reference,
        nom=data.nom,
        secteur=data.secteur,
        puissance=data.puissance,
        tension_mt=data.tension_mt,
        tension_bt=data.tension_bt,
        type_huile=data.type_huile,
        niveau_huile=data.niveau_huile,
        date_installation=data.date_installation,
        etat=data.etat,
        periodicite_inspection_mois=data.periodicite_inspection_mois,
        actif=data.actif,
        localisation=build_point(data.latitude, data.longitude),
    )
    db.add(transformateur)
    db.flush()  # obtient l'id (autoflush désactivé)
    recalculer_prochaine_inspection(db, transformateur)
    db.commit()
    db.refresh(transformateur)
    return transformateur


def update_transformateur(
    db: Session, transformateur: Transformateur, data: TransformateurUpdate
) -> Transformateur:
    values = data.model_dump(exclude_unset=True)
    latitude = values.pop("latitude", None)
    longitude = values.pop("longitude", None)

    nouvelle_periodicite = values.get("periodicite_inspection_mois")
    periodicite_changee = (
        nouvelle_periodicite is not None
        and nouvelle_periodicite != transformateur.periodicite_inspection_mois
    )

    for champ, valeur in values.items():
        if valeur is None and champ not in CHAMPS_NULLABLES:
            continue
        setattr(transformateur, champ, valeur)

    if latitude is not None and longitude is not None:
        transformateur.localisation = build_point(latitude, longitude)

    if periodicite_changee:
        recalculer_prochaine_inspection(db, transformateur)

    db.commit()
    db.refresh(transformateur)
    return transformateur


def delete_transformateur(db: Session, transformateur: Transformateur) -> None:
    db.delete(transformateur)
    db.commit()