from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database.connection import get_db

router = APIRouter(tags=["Santé"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict:
    """Vérifie que l'API, PostgreSQL et PostGIS répondent."""
    try:
        db.execute(text("SELECT 1"))
        postgis_version = db.execute(text("SELECT PostGIS_Lib_Version()")).scalar()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Base de données ou PostGIS indisponible : {exc.__class__.__name__}",
        )

    return {
        "status": "ok",
        "application": settings.APP_NAME,
        "database": "connected",
        "postgis": postgis_version,
    }