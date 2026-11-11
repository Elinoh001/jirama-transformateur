from datetime import date

from pydantic import BaseModel

from app.services.preventive_service import NiveauPriorite


class EcheanceItem(BaseModel):
    transformateur_id: int
    reference: str
    nom: str
    secteur: str
    prochaine_inspection: date  # prochaine inspection prévue (planifiée, sinon échéance théorique)
    jours_restants: int  # négatif = en retard (valeur absolue = jours de retard)
    periodicite_inspection_mois: int
    niveau: NiveauPriorite
    echeance_theorique: date  # dernière inspection réalisée + périodicité
    source: str  # "PLANIFIEE" ou "THEORIQUE" : origine de prochaine_inspection
    en_retard: bool = False
    jours_retard: int = 0


class EcheancesRead(BaseModel):
    en_retard: int  # nombre de postes actifs en retard d'inspection
    items: list[EcheanceItem]
