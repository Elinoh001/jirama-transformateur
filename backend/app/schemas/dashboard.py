from pydantic import BaseModel


class RepartitionPriorites(BaseModel):
    """Nombre de transformateurs actifs par niveau de priorité (graphique en anneau)."""

    normal: int
    a_surveiller: int
    prioritaire: int


class ActiviteMois(BaseModel):
    """Activité d'un mois (graphique en barres). mois au format AAAA-MM."""

    mois: str
    inspections: int
    interventions: int


class DashboardStatistics(BaseModel):
    # Transformateurs
    total_transformateurs: int
    transformateurs_actifs: int
    transformateurs_inactifs: int
    transformateurs_bon: int
    transformateurs_a_surveiller: int
    transformateurs_critiques: int

    # Inspections et interventions
    total_inspections: int
    total_interventions: int
    interventions_planifiees: int
    interventions_en_cours: int
    interventions_terminees: int
    interventions_annulees: int

    # Suivi préventif (transformateurs actifs uniquement)
    nb_priorites: int  # transformateurs actifs au niveau PRIORITAIRE
    repartition_priorites: RepartitionPriorites

    # Données pour les graphiques et indicateurs complémentaires
    activite_mensuelle: list[ActiviteMois]
    cout_total_interventions_terminees: float  # en Ariary