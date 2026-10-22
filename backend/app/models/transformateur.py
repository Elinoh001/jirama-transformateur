import enum
from datetime import date, datetime

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from sqlalchemy import Boolean, Date, DateTime, Enum, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class EtatTransformateur(str, enum.Enum):
    """État technique (santé) du transformateur. Le statut opérationnel est calculé à part."""

    BON = "BON"
    A_SURVEILLER = "A_SURVEILLER"
    CRITIQUE = "CRITIQUE"


class NiveauHuile(str, enum.Enum):
    NORMAL = "NORMAL"
    BAS = "BAS"
    CRITIQUE = "CRITIQUE"


class Transformateur(Base):
    __tablename__ = "transformateurs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reference: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nom: Mapped[str] = mapped_column(String(150), nullable=False)
    secteur: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # quartier
    puissance: Mapped[float] = mapped_column(Float, nullable=False)  # puissance nominale en kVA
    tension_mt: Mapped[float] = mapped_column(Float, nullable=False, default=20.0)  # kV
    tension_bt: Mapped[float] = mapped_column(Float, nullable=False, default=400.0)  # V
    type_huile: Mapped[str | None] = mapped_column(String(100), nullable=True)
    niveau_huile: Mapped[NiveauHuile] = mapped_column(
        Enum(NiveauHuile, native_enum=False, length=20),
        nullable=False,
        default=NiveauHuile.NORMAL,
    )
    date_installation: Mapped[date | None] = mapped_column(Date, nullable=True)
    etat: Mapped[EtatTransformateur] = mapped_column(
        Enum(EtatTransformateur, native_enum=False, length=20),
        nullable=False,
        default=EtatTransformateur.BON,
    )

    # Planification des inspections
    periodicite_inspection_mois: Mapped[int] = mapped_column(Integer, nullable=False, default=12)
    prochaine_inspection: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Colonne PostGIS : POINT en WGS84 (SRID 4326). Un index spatial GiST est créé automatiquement.
    localisation: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )

    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    inspections: Mapped[list["Inspection"]] = relationship(
        back_populates="transformateur",
        cascade="all, delete-orphan",
        order_by="Inspection.date_inspection.desc()",
    )
    interventions: Mapped[list["Intervention"]] = relationship(
        back_populates="transformateur",
        cascade="all, delete-orphan",
        order_by="Intervention.date_intervention.desc()",
    )
    releves: Mapped[list["ReleveCharge"]] = relationship(
        back_populates="transformateur",
        cascade="all, delete-orphan",
        order_by="ReleveCharge.date_releve.desc()",
    )
    pannes: Mapped[list["Panne"]] = relationship(
        back_populates="transformateur",
        cascade="all, delete-orphan",
        order_by="Panne.date_signalement.desc()",
    )

    def __repr__(self) -> str:
        return f"<Transformateur id={self.id} reference={self.reference}>"