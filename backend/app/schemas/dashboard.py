from pydantic import BaseModel


class RepartitionPriorites(BaseModel):
    """Nombre de transformateurs actifs par niveau de priorité (graphique en anneau)."""

    normal: int
    a_surveiller: int
    prioritaire: int


class RepartitionStatuts(BaseModel):
    """Nombre de transformateurs actifs par statut opérationnel."""

    en_service: int
    en_surcharge: int
    en_maintenance: int
    en_panne: int


class SecteurStat(BaseModel):
    """Synthèse d'un secteur/quartier d'Antsirabe (postes actifs)."""

    secteur: str
    total: int
    en_surcharge: int  # postes dont le dernier taux de charge dépasse 100 %
    en_panne: int  # postes au statut opérationnel « en panne »
    pannes_actives: int
    # Centre géographique du secteur, calculé par PostGIS (ST_Centroid)
    latitude_centre: float | None = None
    longitude_centre: float | None = None


class ActiviteMois(BaseModel):
    """Activité d'un mois (graphique en barres). mois au format AAAA-MM."""

    mois: str
    inspections: int
    interventions: int


class DashboardStatistics(BaseModel):
    # Transformateurs (état technique)
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

    # Statut opérationnel, charge et pannes (cahier des charges : tableau de bord décisionnel)
    repartition_statuts: RepartitionStatuts
    taux_charge_moyen: float | None  # moyenne des derniers relevés des postes actifs, None sans relevé
    postes_en_surcharge: int
    pannes_actives: int  # anomalies non résolues (signalées ou en cours)
    pannes_critiques_actives: int
    repartition_secteurs: list[SecteurStat]

    # Données pour les graphiques et indicateurs complémentaires
    activite_mensuelle: list[ActiviteMois]
    cout_total_interventions_terminees: float  # en Ariary
