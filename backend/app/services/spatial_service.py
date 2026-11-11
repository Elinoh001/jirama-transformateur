"""
Requêtes SPATIALES PostGIS (au-delà du simple stockage des coordonnées).

La colonne `transformateurs.localisation` est un POINT en WGS84 (SRID 4326) avec un index GiST.
Fonctions PostGIS utilisées :
  - ST_DWithin / ST_Distance sur le type GEOGRAPHY : recherche par rayon et distance en MÈTRES ;
  - ST_AsGeoJSON : export des géométries pour la cartographie ;
  - ST_MakeEnvelope et l'opérateur && : filtre par emprise (rectangle) sur l'index spatial ;
  - ST_Centroid(ST_Collect(...)) : centre géographique d'un secteur.
"""
import json

from geoalchemy2 import Geography
from sqlalchemy import cast, func, select, String
from sqlalchemy.orm import Session

from app.models.transformateur import Transformateur

SRID_WGS84 = 4326


def _point(latitude: float, longitude: float):
    """Point PostGIS. Attention à l'ordre : ST_MakePoint(longitude, latitude)."""
    return func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), SRID_WGS84)


def transformateurs_proches(
    db: Session,
    latitude: float,
    longitude: float,
    rayon_m: float,
    limit: int = 20,
    actif: bool | None = True,
) -> list[tuple[Transformateur, float]]:
    """Postes situés à moins de `rayon_m` mètres du point donné, du plus proche au plus éloigné."""
    centre = cast(_point(latitude, longitude), Geography)
    localisation = cast(Transformateur.localisation, Geography)
    distance = func.ST_Distance(localisation, centre).label("distance_m")

    stmt = (
        select(Transformateur, distance)
        .where(func.ST_DWithin(localisation, centre, rayon_m))
        .order_by(distance)
        .limit(limit)
    )
    if actif is not None:
        stmt = stmt.where(Transformateur.actif == actif)

    return [(t, float(d)) for t, d in db.execute(stmt).all()]


def geojson_transformateurs(
    db: Session,
    secteur: str | None = None,
    actif: bool | None = None,
    bbox: tuple[float, float, float, float] | None = None,
) -> list[tuple[Transformateur, dict]]:
    """
    Postes avec leur géométrie au format GeoJSON (calculée par PostGIS : ST_AsGeoJSON).
    `bbox` = (lon_min, lat_min, lon_max, lat_max) : seuls les postes dans le rectangle sont renvoyés.
    """
    geom = cast(func.ST_AsGeoJSON(Transformateur.localisation), String).label("geom")
    stmt = select(Transformateur, geom).order_by(Transformateur.reference)

    if secteur:
        stmt = stmt.where(Transformateur.secteur == secteur)
    if actif is not None:
        stmt = stmt.where(Transformateur.actif == actif)
    if bbox is not None:
        lon_min, lat_min, lon_max, lat_max = bbox
        enveloppe = func.ST_MakeEnvelope(lon_min, lat_min, lon_max, lat_max, SRID_WGS84)
        stmt = stmt.where(Transformateur.localisation.op("&&")(enveloppe))

    return [(t, json.loads(g)) for t, g in db.execute(stmt).all()]


def centres_secteurs(db: Session, actif: bool | None = True) -> dict[str, tuple[float, float]]:
    """Centre géographique (latitude, longitude) de chaque secteur : ST_Centroid(ST_Collect(...))."""
    centre = func.ST_Centroid(func.ST_Collect(Transformateur.localisation))
    stmt = select(
        Transformateur.secteur, func.ST_Y(centre), func.ST_X(centre)
    ).group_by(Transformateur.secteur)
    if actif is not None:
        stmt = stmt.where(Transformateur.actif == actif)

    return {secteur: (float(lat), float(lon)) for secteur, lat, lon in db.execute(stmt).all()}
