from typing import Literal

from fastapi import HTTPException, status
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.models.transformateur import EtatTransformateur, Transformateur
from app.schemas.transformateur import (
    HistoriqueEvenement,
    HistoriqueRead,
    PrioriteItem,
    TransformateurCreate,
    TransformateurRead,
    TransformateurUpdate,
)
from app.services import (
    inspection_service,
    intervention_service,
    preventive_service,
    transformateur_service,
)
from app.services.preventive_service import NiveauPriorite, ResultatPriorite


def to_read(t: Transformateur, resultat: ResultatPriorite | None = None) -> TransformateurRead:
    """Convertit la géométrie PostGIS (POINT) en latitude/longitude et ajoute la priorité."""
    point = to_shape(t.localisation)
    return TransformateurRead(
        id=t.id,
        reference=t.reference,
        nom=t.nom,
        secteur=t.secteur,
        puissance=t.puissance,
        tension_mt=t.tension_mt,
        tension_bt=t.tension_bt,
        type_huile=t.type_huile,
        niveau_huile=t.niveau_huile,
        date_installation=t.date_installation,
        etat=t.etat,
        periodicite_inspection_mois=t.periodicite_inspection_mois,
        prochaine_inspection=t.prochaine_inspection,
        latitude=point.y,
        longitude=point.x,
        actif=t.actif,
        created_at=t.created_at,
        updated_at=t.updated_at,
        priorite=resultat.niveau if resultat else None,
        priorite_motifs=resultat.motifs if resultat else [],
        derniere_inspection=resultat.derniere_inspection if resultat else None,
    )


def _to_read_avec_priorite(db: Session, t: Transformateur) -> TransformateurRead:
    return to_read(t, preventive_service.evaluer_transformateur(db, t))


def _get_or_404(db: Session, transformateur_id: int) -> Transformateur:
    t = transformateur_service.get_by_id(db, transformateur_id)
    if t is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transformateur introuvable")
    return t


def list_transformateurs(
    db: Session,
    search: str | None,
    etat: EtatTransformateur | None,
    actif: bool | None,
    skip: int,
    limit: int,
) -> list[TransformateurRead]:
    items = transformateur_service.list_transformateurs(db, search, etat, actif, skip, limit)
    resultats = preventive_service.evaluer_transformateurs(db, items)
    return [to_read(t, resultats[t.id]) for t in items]


def get_transformateur(db: Session, transformateur_id: int) -> TransformateurRead:
    return _to_read_avec_priorite(db, _get_or_404(db, transformateur_id))


def create_transformateur(db: Session, data: TransformateurCreate) -> TransformateurRead:
    if transformateur_service.get_by_reference(db, data.reference):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Un transformateur avec cette référence existe déjà"
        )
    return _to_read_avec_priorite(db, transformateur_service.create_transformateur(db, data))


def update_transformateur(
    db: Session, transformateur_id: int, data: TransformateurUpdate
) -> TransformateurRead:
    t = _get_or_404(db, transformateur_id)

    if data.reference and data.reference != t.reference:
        if transformateur_service.get_by_reference(db, data.reference):
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Un transformateur avec cette référence existe déjà"
            )

    return _to_read_avec_priorite(db, transformateur_service.update_transformateur(db, t, data))


def delete_transformateur(db: Session, transformateur_id: int) -> None:
    t = _get_or_404(db, transformateur_id)
    transformateur_service.delete_transformateur(db, t)


def list_priorites(
    db: Session, niveau: NiveauPriorite | None, inclure_inactifs: bool
) -> list[PrioriteItem]:
    """Liste triée : PRIORITAIRE d'abord, puis A_SURVEILLER, puis NORMAL."""
    actif = None if inclure_inactifs else True
    items = transformateur_service.list_transformateurs(db, actif=actif, limit=1000)
    resultats = preventive_service.evaluer_transformateurs(db, items)

    lignes: list[PrioriteItem] = []
    for t in items:
        r = resultats[t.id]
        if niveau is not None and r.niveau != niveau:
            continue
        point = to_shape(t.localisation)
        lignes.append(
            PrioriteItem(
                transformateur_id=t.id,
                reference=t.reference,
                nom=t.nom,
                puissance=t.puissance,
                etat=t.etat,
                actif=t.actif,
                latitude=point.y,
                longitude=point.x,
                niveau=r.niveau,
                motifs=r.motifs,
                derniere_inspection=r.derniere_inspection,
                jours_depuis_derniere_inspection=r.jours_depuis_derniere_inspection,
            )
        )

    lignes.sort(
        key=lambda ligne: (preventive_service.rang_niveau(ligne.niveau), -len(ligne.motifs), ligne.reference)
    )
    return lignes


def get_historique(
    db: Session, transformateur_id: int, ordre: Literal["asc", "desc"]
) -> HistoriqueRead:
    """Chronologie d'un transformateur : inspections + interventions fusionnées."""
    t = _get_or_404(db, transformateur_id)

    inspections = inspection_service.list_inspections(
        db, transformateur_id=transformateur_id, limit=1000
    )
    interventions = intervention_service.list_interventions(
        db, transformateur_id=transformateur_id, limit=1000
    )

    evenements: list[HistoriqueEvenement] = []
    for i in inspections:
        evenements.append(
            HistoriqueEvenement(
                evenement="INSPECTION",
                id=i.id,
                date_evenement=i.date_inspection,
                type=i.type,
                resume=i.observation,
                technicien=i.technicien,
                etat=i.etat,
            )
        )
    for iv in interventions:
        evenements.append(
            HistoriqueEvenement(
                evenement="INTERVENTION",
                id=iv.id,
                date_evenement=iv.date_intervention,
                type=iv.type,
                resume=iv.description,
                technicien=iv.technicien,
                statut=iv.statut,
                cout=float(iv.cout) if iv.cout is not None else None,
            )
        )

    evenements.sort(key=lambda e: (e.date_evenement, e.id), reverse=(ordre == "desc"))

    return HistoriqueRead(
        transformateur=_to_read_avec_priorite(db, t),
        total=len(evenements),
        evenements=evenements,
    )