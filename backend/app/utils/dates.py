import calendar
from datetime import date


def ajouter_mois(d: date, mois: int) -> date:
    """Ajoute `mois` mois à une date (le jour est ramené à la fin du mois si nécessaire)."""
    index = d.month - 1 + mois
    annee = d.year + index // 12
    mois_final = index % 12 + 1
    jour = min(d.day, calendar.monthrange(annee, mois_final)[1])
    return date(annee, mois_final, jour)