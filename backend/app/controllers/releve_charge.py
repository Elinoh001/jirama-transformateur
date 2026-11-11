from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.releve_charge import ReleveCharge
from app.models.utilisateur import Utilisateur
from app.schemas.releve_charge import ReleveChargeCreate, ReleveChargeRead
from app.services import releve_service, transformateur_service
from app.services.releve_service import TAUX_MAX_COHERENT_POURCENT


def to_read(r: ReleveCharge) -> ReleveChargeRead:
    surcharge = releve_service.est_surcharge(r.taux_charge)
    return ReleveChargeRead(
        id=r.id,
        transformateur_id=r.transformateur_id,
        transformateur_reference=r.transformateur.reference,
        transformateur_nom=r.transformateur.nom,
        date_releve=r.date_releve,
        puissance_mesuree=r.puissance_mesuree,
        courant_mesure=r.courant_mesure,
        puissance_nominale=r.transformateur.puissance,
        taux_charge=r.taux_charge,
        surcharge=surcharge,
        alerte=(
            f"Surcharge : {r.taux_charge:.1f} % de la puissance nominale "
            f"({r.puissance_mesuree:.1f} kVA mesurés pour {r.transformateur.puissance:.1f} kVA)"
            if surcharge
            else None
        ),
        releve_par=r.releve_par,
        created_at=r.created_at,
    )


def list_releves(
    db: Session,
    transformateur_id: int | None,
    surcharge: bool | None,
    date_debut: date | None,
    date_fin: date | None,
    skip: int,
    limit: int,
) -> list[ReleveChargeRead]:
    items = releve_service.list_releves(db, transformateur_id, surcharge, date_debut, date_fin, skip, limit)
    return [to_read(r) for r in items]


def get_releve(db: Session, releve_id: int) -> ReleveChargeRead:
    releve = releve_service.get_by_id(db, releve_id)
    if releve is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Relevé introuvable")
    return to_read(releve)


def create_releve(db: Session, data: ReleveChargeCreate, current_user: Utilisateur) -> ReleveChargeRead:
    transformateur = transformateur_service.get_by_id(db, data.transformateur_id)
    if transformateur is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transformateur introuvable")

    # Mesure incohérente : refusée avant tout calcul ou enregistrement.
    puissance = (
        data.puissance_mesuree
        if data.puissance_mesuree is not None
        else releve_service.puissance_depuis_courant(data.courant_mesure, transformateur.tension_bt)
    )
    taux = puissance / transformateur.puissance * 100
    if taux > TAUX_MAX_COHERENT_POURCENT:
        raise HTTPException(
            422,
            f"Mesure incohérente : {taux:.0f} % de la puissance nominale "
            f"(maximum accepté : {TAUX_MAX_COHERENT_POURCENT:.0f} %). Vérifiez la valeur et l'unité (kVA ou A).",
        )

    releve_par = data.releve_par or f"{current_user.prenom} {current_user.nom}"
    return to_read(releve_service.create_releve(db, transformateur, data, releve_par))
