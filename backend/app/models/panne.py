import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TypePanne(str, enum.Enum):
    FUITE_HUILE = "FUITE_HUILE"
    SURCHAUFFE = "SURCHAUFFE"
    COUPURE = "COUPURE"
    ANOMALIE_MECANIQUE = "ANOMALIE_MECANIQUE"


class GravitePanne(str, enum.Enum):
    MINEURE = "MINEURE"
    MAJEURE = "MAJEURE"
    CRITIQUE = "CRITIQUE"


class StatutPanne(str, enum.Enum):
    SIGNALEE = "SIGNALEE"
    EN_COURS = "EN_COURS"
    RESOLUE = "RESOLUE"


class Panne(Base):
    __tablename__ = "pannes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transformateur_id: Mapped[int] = mapped_column(
        ForeignKey("transformateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type_panne: Mapped[TypePanne] = mapped_column(
        Enum(TypePanne, native_enum=False, length=30), nullable=False
    )
    gravite: Mapped[GravitePanne] = mapped_column(
        Enum(GravitePanne, native_enum=False, length=20), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    statut: Mapped[StatutPanne] = mapped_column(
        Enum(StatutPanne, native_enum=False, length=20),
        nullable=False,
        default=StatutPanne.SIGNALEE,
    )
    signale_par: Mapped[str] = mapped_column(String(150), nullable=False)
    date_signalement: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Renseignés à la clôture (obligatoires pour passer à RESOLUE : règle appliquée à l'étape 12)
    date_resolution: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actions_correctives: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolu_par: Mapped[str | None] = mapped_column(String(150), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    transformateur: Mapped["Transformateur"] = relationship(back_populates="pannes")

    def __repr__(self) -> str:
        return f"<Panne id={self.id} transformateur_id={self.transformateur_id} statut={self.statut.value}>"