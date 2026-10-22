"""Référentiels métier : secteurs d'Antsirabe, zone géographique, périodicité par défaut."""

# Liste FICTIVE : à remplacer par la liste officielle des quartiers/secteurs de la JIRAMA.
SECTEURS_ANTSIRABE: list[str] = [
    "Centre-ville",
    "Ambalavola",
    "Antanambao",
    "Mahazoarivo",
    "Tsarasaotra",
    "Andranomanelatra",
    "Soanindrarina",
    "Ambohimena",
]

# Boîte englobante (WGS84) de l'agglomération d'Antsirabe et de ses environs.
ZONE_ANTSIRABE = {
    "lat_min": -20.05,
    "lat_max": -19.70,
    "lon_min": 46.90,
    "lon_max": 47.20,
}

PERIODICITE_INSPECTION_MOIS_DEFAUT = 12


def normaliser_secteur(valeur: str) -> str:
    """Retourne le secteur tel qu'écrit dans la liste (insensible à la casse), sinon lève ValueError."""
    cherche = valeur.strip().lower()
    for secteur in SECTEURS_ANTSIRABE:
        if secteur.lower() == cherche:
            return secteur
    raise ValueError(f"secteur inconnu, valeurs possibles : {', '.join(SECTEURS_ANTSIRABE)}")


def point_dans_zone(latitude: float, longitude: float) -> bool:
    z = ZONE_ANTSIRABE
    return z["lat_min"] <= latitude <= z["lat_max"] and z["lon_min"] <= longitude <= z["lon_max"]