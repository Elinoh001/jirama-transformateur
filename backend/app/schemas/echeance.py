from datetime import date

from pydantic import BaseModel

from app.services.preventive_service import NiveauPriorite


class EcheanceItem(BaseModel):
    transformateur_id: int
    reference: str
    nom: str
    secteur: str
    prochaine_inspection: date
    jours_restants: int  # négatif = échéance dépassée
    periodicite_inspection_mois: int
    niveau: NiveauPriorite


class EcheancesRead(BaseModel):
    en_retard: int  # nombre de postes actifs dont l'échéance est dépassée
    items: list[EcheanceItem]