from sqlalchemy.orm import Session

from app.controllers import transformateur as transformateur_controller
from app.schemas.dashboard import DashboardStatistics
from app.schemas.echeance import EcheancesRead
from app.schemas.transformateur import PrioriteItem
from app.services import dashboard_service, echeance_service
from app.services.preventive_service import NiveauPriorite


def get_statistics(db: Session) -> DashboardStatistics:
    return dashboard_service.get_statistics(db)


def get_priorities(
    db: Session,
    niveau: NiveauPriorite | None,
    inclure_normal: bool,
    limit: int,
) -> list[PrioriteItem]:
    """
    Priorités affichées sur le dashboard : transformateurs actifs, triés du plus urgent
    au moins urgent. Sans filtre, les transformateurs NORMAL sont exclus.
    """
    items = transformateur_controller.list_priorites(db, niveau, inclure_inactifs=False)
    if niveau is None and not inclure_normal:
        items = [i for i in items if i.niveau != NiveauPriorite.NORMAL]
    return items[:limit]


def get_prochaines_inspections(db: Session, limit: int) -> EcheancesRead:
    return echeance_service.prochaines_inspections(db, limit)