from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ReleveCharge(Base):
    """Mesure de charge d'un transformateur. Le taux est calculé à la saisie (étape 12)."""

    __tablename__ = "releves_charge"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transformateur_id: Mapped[int] = mapped_column(
        ForeignKey("transformateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date_releve: Mapped[date] = mapped_column(Date, nullable=False)
    puissance_mesuree: Mapped[float] = mapped_column(Float, nullable=False)  # kVA
    courant_mesure: Mapped[float | None] = mapped_column(Float, nullable=True)  # A
    # (puissance_mesuree / puissance nominale) * 100, figé au moment du relevé
    taux_charge: Mapped[float] = mapped_column(Float, nullable=False)
    releve_par: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    transformateur: Mapped["Transformateur"] = relationship(back_populates="releves")

    def __repr__(self) -> str:
        return f"<ReleveCharge id={self.id} transformateur_id={self.transformateur_id} taux={self.taux_charge}>"