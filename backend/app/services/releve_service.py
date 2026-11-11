import math
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.releve_charge import ReleveCharge
from app.models.transformateur import Transformateur
from app.schemas.releve_charge import ReleveChargeCreate
from app.services.statut_service import SEUIL_SURCHARGE_POURCENT

# Au-delà de 3 fois la puissance nominale, la mesure est considérée comme incohérente
# (erreur de saisie probable) et le relevé est refusé.
TAUX_MAX_COHERENT_POURCENT = 300.0


def puissance_depuis_courant(courant_a: float, tension_bt_v: float) -> float:
    """Puissance apparente triphasée en kVA : S = racine(3) x U (V) x I (A) / 1000."""
    return math.sqrt(3) * tension_bt_v * courant_a / 1000


def calculer_taux(puissance_mesuree_kva: float, puissance_nominale_kva: float) -> float:
    """Taux de charge (%) = (puissance mesurée / puissance nominale) x 100."""
    return round(puissance_mesuree_kva / puissance_nominale_kva * 100, 2)


def est_surcharge(taux_charge: float) -> bool:
    return taux_charge > SEUIL_SURCHARGE_POURCENT


def get_by_id(db: Session, releve_id: int) -> ReleveCharge | None:
    return db.get(ReleveCharge, releve_id)


def list_releves(
    db: Session,
    transformateur_id: int | None = None,
    surcharge: bool | None = None,
    date_debut: date | None = None,
    date_fin: date | None = None,
    skip: int = 0,
    limit: int = 500,
) -> list[ReleveCharge]:
    stmt = (
        select(ReleveCharge)
        .options(joinedload(ReleveCharge.transformateur))
        .order_by(ReleveCharge.date_releve.desc(), ReleveCharge.id.desc())
    )
    if transformateur_id is not None:
        stmt = stmt.where(ReleveCharge.transformateur_id == transformateur_id)
    if surcharge is True:
        stmt = stmt.where(ReleveCharge.taux_charge > SEUIL_SURCHARGE_POURCENT)
    elif surcharge is False:
        stmt = stmt.where(ReleveCharge.taux_charge <= SEUIL_SURCHARGE_POURCENT)
    if date_debut is not None:
        stmt = stmt.where(ReleveCharge.date_releve >= date_debut)
    if date_fin is not None:
        stmt = stmt.where(ReleveCharge.date_releve <= date_fin)

    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_releve(
    db: Session, transformateur: Transformateur, data: ReleveChargeCreate, releve_par: str
) -> ReleveCharge:
    """Calcule la puissance (si seul le courant est saisi) puis le taux de charge, et enregistre."""
    if data.puissance_mesuree is not None:
        puissance = data.puissance_mesuree
    else:
        puissance = round(puissance_depuis_courant(data.courant_mesure, transformateur.tension_bt), 2)

    releve = ReleveCharge(
        transformateur_id=transformateur.id,
        date_releve=data.date_releve,
        puissance_mesuree=puissance,
        courant_mesure=data.courant_mesure,
        taux_charge=calculer_taux(puissance, transformateur.puissance),
        releve_par=releve_par,
    )
    db.add(releve)
    db.commit()
    db.refresh(releve)
    return releve


def recalculer_taux_transformateur(transformateur: Transformateur) -> None:
    """À appeler si la puissance nominale change : remet les taux historiques à jour (sans commit)."""
    for releve in transformateur.releves:
        releve.taux_charge = calculer_taux(releve.puissance_mesuree, transformateur.puissance)
