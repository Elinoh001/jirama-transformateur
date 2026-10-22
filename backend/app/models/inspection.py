import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.transformateur import EtatTransformateur


class StatutInspection(str, enum.Enum):
    PLANIFIEE = "PLANIFIEE"
    REALISEE = "REALISEE"
    ANNULEE = "ANNULEE"


class EtatHuile(str, enum.Enum):
    BONNE = "BONNE"
    DEGRADEE = "DEGRADEE"
    CONTAMINEE = "CONTAMINEE"


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transformateur_id: Mapped[int] = mapped_column(
        ForeignKey("transformateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Date réalisée (statut REALISEE) ou date programmée (statut PLANIFIEE).
    date_inspection: Mapped[date] = mapped_column(Date, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # nature : ROUTINE, VISUELLE, THERMIQUE...
    statut: Mapped[StatutInspection] = mapped_column(
        Enum(StatutInspection, native_enum=False, length=20),
        nullable=False,
        default=StatutInspection.REALISEE,
    )
    # État constaté : renseigné seulement pour une inspection réalisée.
    etat: Mapped[EtatTransformateur | None] = mapped_column(
        Enum(EtatTransformateur, native_enum=False, length=20), nullable=True
    )
    etat_huile: Mapped[EtatHuile | None] = mapped_column(
        Enum(EtatHuile, native_enum=False, length=20), nullable=True
    )
    observation: Mapped[str | None] = mapped_column(Text, nullable=True)
    technicien: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    transformateur: Mapped["Transformateur"] = relationship(back_populates="inspections")

    def __repr__(self) -> str:
        return f"<Inspection id={self.id} transformateur_id={self.transformateur_id}>"