from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.intervention import Intervention, StatutIntervention
from app.models.utilisateur import Utilisateur
from app.schemas.intervention import InterventionCreate, InterventionRead, InterventionUpdate
from app.services import intervention_service, transformateur_service

S = StatutIntervention

# Cycle de vie : PLANIFIEE -> EN_COURS -> TERMINEE, et annulation possible avant la fin.
# TERMINEE et ANNULEE sont définitives.
TRANSITIONS_AUTORISEES = {
    S.PLANIFIEE: {S.PLANIFIEE, S.EN_COURS, S.TERMINEE, S.ANNULEE},
    S.EN_COURS: {S.EN_COURS, S.TERMINEE, S.ANNULEE},
}
# Seuls champs qu'on peut compléter après la fin d'une intervention.
CHAMPS_MODIFIABLES_SI_TERMINEE = {"description", "cout"}
# Champs que le client peut envoyer à null pour les effacer (les autres null sont ignorés).
CHAMPS_NULLABLES = {"description", "cout"}


def _erreur(message: str) -> HTTPException:
    return HTTPException(422, message)


def _conflit(message: str) -> HTTPException:
    return HTTPException(status.HTTP_409_CONFLICT, message)


def to_read(i: Intervention) -> InterventionRead:
    en_retard = i.statut == S.PLANIFIEE and i.date_intervention < date.today()
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
        en_retard=en_retard,
        jours_retard=(date.today() - i.date_intervention).days if en_retard else 0,
    )


def _get_or_404(db: Session, intervention_id: int) -> Intervention:
    intervention = intervention_service.get_by_id(db, intervention_id)
    if intervention is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Intervention introuvable")
    return intervention


def _champs_modifies(intervention: Intervention, champs: dict) -> set[str]:
    """Champs dont la valeur envoyée DIFFÈRE de la valeur enregistrée (les formulaires renvoient tout)."""
    modifies = set()
    for champ, valeur in champs.items():
        if valeur is None and champ not in CHAMPS_NULLABLES:
            continue
        if valeur != getattr(intervention, champ):
            modifies.add(champ)
    return modifies


def list_interventions(
    db: Session,
    transformateur_id: int | None,
    statut: StatutIntervention | None,
    skip: int,
    limit: int,
    en_retard: bool | None = None,
) -> list[InterventionRead]:
    items = intervention_service.list_interventions(db, transformateur_id, statut, skip, limit, en_retard)
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
    champs = data.model_dump(exclude_unset=True)
    actuel = intervention.statut

    # --- Intervention annulée : archivée ---
    if actuel == S.ANNULEE:
        raise _conflit(
            "Une intervention annulée est archivée et ne peut plus être modifiée. "
            "Planifiez-en une nouvelle si nécessaire."
        )

    # --- Intervention terminée : figée (le compte-rendu et le coût peuvent être complétés) ---
    if actuel == S.TERMINEE:
        interdits = _champs_modifies(intervention, champs) - CHAMPS_MODIFIABLES_SI_TERMINEE
        if interdits:
            raise _conflit(
                "Une intervention terminée est figée pour conserver l'historique d'entretien : elle ne peut "
                f"être ni annulée, ni rouverte, ni replanifiée (champs refusés : {', '.join(sorted(interdits))}). "
                "Seuls la description et le coût peuvent être complétés."
            )
        if "description" in champs and not (champs["description"] or "").strip():
            raise _erreur("Le compte-rendu d'une intervention terminée ne peut pas être vide")
        return to_read(intervention_service.update_intervention(db, intervention, data))

    # --- Intervention planifiée ou en cours ---
    statut_final = data.statut or actuel
    if statut_final not in TRANSITIONS_AUTORISEES[actuel]:
        raise _conflit(
            f"Changement de statut impossible : {actuel.value} -> {statut_final.value}. "
            "Cycle autorisé : PLANIFIEE -> EN_COURS -> TERMINEE (annulation possible avant la fin)."
        )

    date_finale = data.date_intervention or intervention.date_intervention
    description_finale = champs["description"] if "description" in champs else intervention.description

    if statut_final in (S.EN_COURS, S.TERMINEE):
        if date_finale > date.today():
            raise _erreur(
                "Une intervention commencée ou terminée ne peut pas avoir une date future : "
                "indiquez la date réelle de l'intervention"
            )
        if statut_final == S.TERMINEE and not (description_finale or "").strip():
            raise _erreur("Le compte-rendu (description) est obligatoire pour terminer une intervention")
    elif statut_final == S.PLANIFIEE:
        if data.date_intervention is not None and data.date_intervention < date.today():
            raise _erreur("Impossible de planifier une intervention à une date passée")

    return to_read(intervention_service.update_intervention(db, intervention, data))
