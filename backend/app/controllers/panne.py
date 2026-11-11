from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.panne import GravitePanne, Panne, StatutPanne
from app.models.utilisateur import Utilisateur
from app.schemas.panne import PanneCreate, PanneRead, PanneUpdate
from app.services import panne_service, transformateur_service


def _erreur(message: str) -> HTTPException:
    return HTTPException(422, message)


def _nom(user: Utilisateur) -> str:
    return f"{user.prenom} {user.nom}"


def to_read(p: Panne) -> PanneRead:
    return PanneRead(
        id=p.id,
        transformateur_id=p.transformateur_id,
        transformateur_reference=p.transformateur.reference,
        transformateur_nom=p.transformateur.nom,
        secteur=p.transformateur.secteur,
        type_panne=p.type_panne,
        gravite=p.gravite,
        description=p.description,
        statut=p.statut,
        active=p.statut != StatutPanne.RESOLUE,
        signale_par=p.signale_par,
        date_signalement=p.date_signalement,
        date_resolution=p.date_resolution,
        actions_correctives=p.actions_correctives,
        resolu_par=p.resolu_par,
        updated_at=p.updated_at,
    )


def _get_or_404(db: Session, panne_id: int) -> Panne:
    panne = panne_service.get_by_id(db, panne_id)
    if panne is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Panne introuvable")
    return panne


def list_pannes(
    db: Session,
    transformateur_id: int | None,
    statut: StatutPanne | None,
    gravite: GravitePanne | None,
    active: bool | None,
    skip: int,
    limit: int,
) -> list[PanneRead]:
    items = panne_service.list_pannes(db, transformateur_id, statut, gravite, active, skip, limit)
    return [to_read(p) for p in items]


def get_panne(db: Session, panne_id: int) -> PanneRead:
    return to_read(_get_or_404(db, panne_id))


def create_panne(db: Session, data: PanneCreate, current_user: Utilisateur) -> PanneRead:
    if transformateur_service.get_by_id(db, data.transformateur_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transformateur introuvable")
    return to_read(panne_service.create_panne(db, data, _nom(current_user)))


def update_panne(
    db: Session, panne_id: int, data: PanneUpdate, current_user: Utilisateur
) -> PanneRead:
    panne = _get_or_404(db, panne_id)

    # Règle : une panne résolue est figée (le rapport de clôture fait foi).
    if panne.statut == StatutPanne.RESOLUE:
        raise HTTPException(status.HTTP_409_CONFLICT, "Une panne résolue ne peut plus être modifiée")

    # Transitions autorisées : SIGNALEE -> EN_COURS -> RESOLUE (ou SIGNALEE -> RESOLUE).
    if data.statut == StatutPanne.SIGNALEE and panne.statut == StatutPanne.EN_COURS:
        raise _erreur("Une panne en cours d'intervention ne peut pas redevenir « signalée »")

    # Règle 6 : pas de clôture sans rapport d'actions correctives.
    if data.statut == StatutPanne.RESOLUE:
        rapport = data.actions_correctives or panne.actions_correctives or ""
        if not rapport.strip():
            raise _erreur("Le rapport des actions correctives est obligatoire pour clôturer la panne")

    # Le statut opérationnel du transformateur est calculé à la lecture à partir des pannes
    # actives (statut_service) : il n'y a donc rien à resynchroniser ici.
    return to_read(panne_service.update_panne(db, panne, data, _nom(current_user)))
