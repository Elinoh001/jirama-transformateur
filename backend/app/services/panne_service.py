from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.panne import GravitePanne, Panne, StatutPanne
from app.schemas.panne import PanneCreate, PanneUpdate


def get_by_id(db: Session, panne_id: int) -> Panne | None:
    return db.get(Panne, panne_id)


def list_pannes(
    db: Session,
    transformateur_id: int | None = None,
    statut: StatutPanne | None = None,
    gravite: GravitePanne | None = None,
    active: bool | None = None,
    skip: int = 0,
    limit: int = 500,
) -> list[Panne]:
    stmt = (
        select(Panne)
        .options(joinedload(Panne.transformateur))
        .order_by(Panne.date_signalement.desc(), Panne.id.desc())
    )
    if transformateur_id is not None:
        stmt = stmt.where(Panne.transformateur_id == transformateur_id)
    if statut is not None:
        stmt = stmt.where(Panne.statut == statut)
    if gravite is not None:
        stmt = stmt.where(Panne.gravite == gravite)
    if active is True:
        stmt = stmt.where(Panne.statut != StatutPanne.RESOLUE)
    elif active is False:
        stmt = stmt.where(Panne.statut == StatutPanne.RESOLUE)

    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_panne(db: Session, data: PanneCreate, signale_par: str) -> Panne:
    panne = Panne(
        transformateur_id=data.transformateur_id,
        type_panne=data.type_panne,
        gravite=data.gravite,
        description=data.description,
        statut=StatutPanne.SIGNALEE,
        signale_par=signale_par,
    )
    db.add(panne)
    db.commit()
    db.refresh(panne)
    return panne


def update_panne(db: Session, panne: Panne, data: PanneUpdate, utilisateur: str) -> Panne:
    """Applique les modifications. Les règles de validité sont vérifiées par le contrôleur."""
    values = data.model_dump(exclude_unset=True)

    if values.get("gravite") is not None:
        panne.gravite = values["gravite"]
    if values.get("description") is not None:
        panne.description = values["description"]
    if "actions_correctives" in values and values["actions_correctives"] is not None:
        panne.actions_correctives = values["actions_correctives"]

    nouveau_statut = values.get("statut")
    if nouveau_statut is not None and nouveau_statut != panne.statut:
        panne.statut = nouveau_statut
        if nouveau_statut == StatutPanne.RESOLUE:
            panne.date_resolution = datetime.now(timezone.utc)
            panne.resolu_par = utilisateur

    db.commit()
    db.refresh(panne)
    return panne
