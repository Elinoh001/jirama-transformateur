import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class StatutIntervention(str, enum.Enum):
    PLANIFIEE = "PLANIFIEE"
    EN_COURS = "EN_COURS"
    TERMINEE = "TERMINEE"
    ANNULEE = "ANNULEE"


class Intervention(Base):
    __tablename__ = "interventions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transformateur_id: Mapped[int] = mapped_column(
        ForeignKey("transformateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date_intervention: Mapped[date] = mapped_column(Date, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # ex: PREVENTIVE, CORRECTIVE
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cout: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)  # en Ariary
    statut: Mapped[StatutIntervention] = mapped_column(
        Enum(StatutIntervention, native_enum=False, length=20),
        nullable=False,
        default=StatutIntervention.PLANIFIEE,
    )
    technicien: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    transformateur: Mapped["Transformateur"] = relationship(back_populates="interventions")

    def __repr__(self) -> str:
        return f"<Intervention id={self.id} transformateur_id={self.transformateur_id}>"