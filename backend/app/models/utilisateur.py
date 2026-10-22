import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class RoleUtilisateur(str, enum.Enum):
    ADMIN = "ADMIN"
    SUPERVISEUR = "SUPERVISEUR"
    AGENT = "AGENT"


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    mot_de_passe: Mapped[str] = mapped_column(String(255), nullable=False)  # hash bcrypt
    role: Mapped[RoleUtilisateur] = mapped_column(
        Enum(RoleUtilisateur, native_enum=False, length=20),
        nullable=False,
        default=RoleUtilisateur.AGENT,
    )
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Utilisateur id={self.id} email={self.email} role={self.role.value}>"