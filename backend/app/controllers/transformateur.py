from typing import Literal

from fastapi import HTTPException, status
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.config.referentiels import SECTEURS_ANTSIRABE
from app.models.transformateur import EtatTransformateur, Transformateur
from app.schemas.transformateur import (
    HistoriqueEvenement,
    HistoriqueRead,
    PrioriteItem,
    ProcheItem,
    TransformateurCreate,
    TransformateurRead,
    TransformateurUpdate,
)
from app.services import (
    inspection_service,
    intervention_service,
    panne_service,
    preventive_service,
    spatial_service,
    statut_service,
    transformateur_service,
)
from app.services.preventive_service import NiveauPriorite, ResultatPriorite
from app.services.statut_service import SituationPoste, StatutOperationnel

LIMITE_MAX = 1000


def to_read(
    t: Transformateur,
    resultat: ResultatPriorite | None = None,
    situation: SituationPoste | None = None,
) -> TransformateurRead:
    """Convertit la géométrie PostGIS (POINT) en latitude/longitude et ajoute priorité et statut."""
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
        prochaine_inspection=(
            (resultat.prochaine_planifiee or resultat.echeance_theorique) or t.prochaine_inspection
            if resultat
            else t.prochaine_inspection
        ),
        latitude=point.y,
        longitude=point.x,
        actif=t.actif,
        created_at=t.created_at,
        updated_at=t.updated_at,
        priorite=resultat.niveau if resultat else None,
        priorite_motifs=resultat.motifs if resultat else [],
        derniere_inspection=resultat.derniere_inspection if resultat else None,
        echeance_theorique=resultat.echeance_theorique if resultat else None,
        prochaine_inspection_planifiee=resultat.prochaine_planifiee if resultat else None,
        inspection_en_retard=resultat.jours_retard_inspection > 0 if resultat else False,
        jours_retard_inspection=resultat.jours_retard_inspection if resultat else 0,
        statut_operationnel=situation.statut if situation else None,
        nb_pannes_actives=situation.nb_pannes_actives if situation else 0,
        taux_charge=situation.taux_charge if situation else None,
    )


def _to_read_complet(db: Session, t: Transformateur) -> TransformateurRead:
    """Un transformateur avec sa situation (pannes, charge) et sa priorité préventive."""
    situation = statut_service.evaluer_poste(db, t.id)
    resultat = preventive_service.evaluer_transformateurs(db, [t], {t.id: situation})[t.id]
    return to_read(t, resultat, situation)


def _get_or_404(db: Session, transformateur_id: int) -> Transformateur:
    t = transformateur_service.get_by_id(db, transformateur_id)
    if t is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transformateur introuvable")
    return t


def list_secteurs() -> list[str]:
    return list(SECTEURS_ANTSIRABE)


def list_transformateurs(
    db: Session,
    search: str | None,
    etat: EtatTransformateur | None,
    actif: bool | None,
    secteur: str | None,
    statut_operationnel: StatutOperationnel | None,
    skip: int,
    limit: int,
) -> list[TransformateurRead]:
    if statut_operationnel is None:
        items = transformateur_service.list_transformateurs(db, search, etat, actif, secteur, skip, limit)
        situations = statut_service.evaluer_postes(db, [t.id for t in items])
    else:
        # Le statut opérationnel est calculé (non stocké) : on filtre après calcul, puis on pagine.
        candidats = transformateur_service.list_transformateurs(
            db, search, etat, actif, secteur, 0, LIMITE_MAX
        )
        toutes = statut_service.evaluer_postes(db, [t.id for t in candidats])
        retenus = [t for t in candidats if toutes[t.id].statut == statut_operationnel]
        items = retenus[skip : skip + limit]
        situations = {t.id: toutes[t.id] for t in items}

    resultats = preventive_service.evaluer_transformateurs(db, items, situations)
    return [to_read(t, resultats[t.id], situations[t.id]) for t in items]


def get_transformateur(db: Session, transformateur_id: int) -> TransformateurRead:
    return _to_read_complet(db, _get_or_404(db, transformateur_id))


def create_transformateur(db: Session, data: TransformateurCreate) -> TransformateurRead:
    if transformateur_service.get_by_reference(db, data.reference):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Un transformateur avec cette référence existe déjà"
        )
    return _to_read_complet(db, transformateur_service.create_transformateur(db, data))


def update_transformateur(
    db: Session, transformateur_id: int, data: TransformateurUpdate
) -> TransformateurRead:
    t = _get_or_404(db, transformateur_id)

    if data.reference and data.reference != t.reference:
        if transformateur_service.get_by_reference(db, data.reference):
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Un transformateur avec cette référence existe déjà"
            )

    return _to_read_complet(db, transformateur_service.update_transformateur(db, t, data))


def delete_transformateur(db: Session, transformateur_id: int) -> None:
    t = _get_or_404(db, transformateur_id)
    transformateur_service.delete_transformateur(db, t)


def list_priorites(
    db: Session, niveau: NiveauPriorite | None, inclure_inactifs: bool
) -> list[PrioriteItem]:
    """Liste triée : PRIORITAIRE d'abord, puis A_SURVEILLER, puis NORMAL."""
    actif = None if inclure_inactifs else True
    items = transformateur_service.list_transformateurs(db, actif=actif, limit=LIMITE_MAX)
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
                jours_retard_inspection=r.jours_retard_inspection,
            )
        )

    lignes.sort(
        key=lambda ligne: (preventive_service.rang_niveau(ligne.niveau), -len(ligne.motifs), ligne.reference)
    )
    return lignes


# ----------------------------------------------------------------------------------------------
# Fonctions spatiales (PostGIS)
# ----------------------------------------------------------------------------------------------
def list_proches(
    db: Session, latitude: float, longitude: float, rayon_m: float, limit: int, inclure_inactifs: bool
) -> list[ProcheItem]:
    """Postes situés dans un rayon (en mètres) autour d'un point, du plus proche au plus éloigné."""
    resultats = spatial_service.transformateurs_proches(
        db, latitude, longitude, rayon_m, limit, actif=None if inclure_inactifs else True
    )
    situations = statut_service.evaluer_postes(db, [t.id for t, _ in resultats])
    lignes: list[ProcheItem] = []
    for t, distance in resultats:
        point = to_shape(t.localisation)
        lignes.append(
            ProcheItem(
                transformateur_id=t.id,
                reference=t.reference,
                nom=t.nom,
                secteur=t.secteur,
                distance_m=round(distance, 1),
                latitude=point.y,
                longitude=point.x,
                statut_operationnel=situations[t.id].statut,
            )
        )
    return lignes


def _lire_bbox(bbox: str | None) -> tuple[float, float, float, float] | None:
    if bbox is None:
        return None
    try:
        lon_min, lat_min, lon_max, lat_max = (float(v) for v in bbox.split(","))
    except ValueError:
        raise HTTPException(
            422,
            "bbox invalide : format attendu lon_min,lat_min,lon_max,lat_max",
        )
    if lon_min >= lon_max or lat_min >= lat_max:
        raise HTTPException(
            422, "bbox invalide : les minimums doivent être inférieurs aux maximums"
        )
    return lon_min, lat_min, lon_max, lat_max


def geojson(db: Session, secteur: str | None, actif: bool | None, bbox: str | None) -> dict:
    """FeatureCollection GeoJSON des postes (géométrie produite par PostGIS)."""
    lignes = spatial_service.geojson_transformateurs(db, secteur, actif, _lire_bbox(bbox))
    situations = statut_service.evaluer_postes(db, [t.id for t, _ in lignes])
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": geometrie,
                "properties": {
                    "id": t.id,
                    "reference": t.reference,
                    "nom": t.nom,
                    "secteur": t.secteur,
                    "puissance": t.puissance,
                    "actif": t.actif,
                    "statut_operationnel": situations[t.id].statut.value,
                    "taux_charge": situations[t.id].taux_charge,
                },
            }
            for t, geometrie in lignes
        ],
    }


# ----------------------------------------------------------------------------------------------
# Carnet d'entretien : historique chronologique
# ----------------------------------------------------------------------------------------------
def get_historique(
    db: Session, transformateur_id: int, ordre: Literal["asc", "desc"]
) -> HistoriqueRead:
    """Chronologie d'un transformateur : inspections, interventions et pannes fusionnées."""
    t = _get_or_404(db, transformateur_id)

    inspections = inspection_service.list_inspections(
        db, transformateur_id=transformateur_id, limit=LIMITE_MAX
    )
    interventions = intervention_service.list_interventions(
        db, transformateur_id=transformateur_id, limit=LIMITE_MAX
    )
    pannes = panne_service.list_pannes(db, transformateur_id=transformateur_id, limit=LIMITE_MAX)

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
                statut=i.statut.value,
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
                statut=iv.statut.value,
                cout=float(iv.cout) if iv.cout is not None else None,
            )
        )
    for p in pannes:
        evenements.append(
            HistoriqueEvenement(
                evenement="PANNE",
                id=p.id,
                date_evenement=p.date_signalement.date(),
                type=p.type_panne.value,
                resume=p.description,
                technicien=p.signale_par,
                statut=p.statut.value,
                gravite=p.gravite,
            )
        )

    evenements.sort(key=lambda e: (e.date_evenement, e.id), reverse=(ordre == "desc"))

    return HistoriqueRead(
        transformateur=_to_read_complet(db, t),
        total=len(evenements),
        evenements=evenements,
    )
