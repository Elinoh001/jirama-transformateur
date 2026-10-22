"""
Fixtures communes.

Les tests utilisent une base SÉPARÉE (jirama_test_db), créée automatiquement avec PostGIS.
La base de développement jirama_db n'est jamais modifiée.
"""
from collections.abc import Callable, Generator
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

import app.models as _models  # noqa: F401  (enregistre les modèles dans Base.metadata)
from app.config.security import create_access_token, hash_password
from app.config.settings import settings
from app.database.base import Base
from app.database.connection import get_db
from app.main import app
from app.models.utilisateur import RoleUtilisateur, Utilisateur

TEST_DB_NAME = "jirama_test_db"
PASSWORD = "Test1234!"
_PASSWORD_HASH = hash_password(PASSWORD)  # calculé une seule fois (bcrypt est volontairement lent)
_TEST_URL = make_url(settings.DATABASE_URL).set(database=TEST_DB_NAME)

# (prénom, nom, email, rôle) -> ids 1, 2, 3 après chaque remise à zéro
_UTILISATEURS = [
    ("Admin", "Test", "admin@jirama.local", RoleUtilisateur.ADMIN),
    ("Superviseur", "Test", "superviseur@jirama.local", RoleUtilisateur.SUPERVISEUR),
    ("Agent", "Test", "agent@jirama.local", RoleUtilisateur.AGENT),
]


@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    # 1) créer la base de test si elle n'existe pas
    admin_engine = create_engine(_TEST_URL.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        existe = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": TEST_DB_NAME}
        ).scalar()
        if not existe:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin_engine.dispose()

    # 2) activer PostGIS et créer les tables
    eng = create_engine(_TEST_URL, pool_pre_ping=True)
    with eng.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.create_all(eng)

    yield eng
    eng.dispose()


@pytest.fixture(autouse=True)
def reset_db(engine: Engine) -> None:
    """Avant chaque test : base vide + 3 utilisateurs (ids 1, 2, 3)."""
    assert engine.url.database == TEST_DB_NAME, "Sécurité : jamais de TRUNCATE hors base de test"
    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE TABLE inspections, interventions, transformateurs, utilisateurs "
                "RESTART IDENTITY CASCADE"
            )
        )
    with Session(engine) as s:
        for prenom, nom, email, role in _UTILISATEURS:
            s.add(
                Utilisateur(
                    nom=nom,
                    prenom=prenom,
                    email=email,
                    mot_de_passe=_PASSWORD_HASH,
                    role=role,
                    actif=True,
                )
            )
            s.flush()  # garantit l'ordre des ids
        s.commit()


@pytest.fixture
def client(engine: Engine) -> Generator[TestClient, None, None]:
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db(engine: Engine) -> Generator[Session, None, None]:
    """Session directe sur la base de test (pour vérifier le contenu en SQL)."""
    with Session(engine) as s:
        yield s


def _headers(user_id: int, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id, role)}"}


@pytest.fixture
def admin_h() -> dict[str, str]:
    return _headers(1, "ADMIN")


@pytest.fixture
def sup_h() -> dict[str, str]:
    return _headers(2, "SUPERVISEUR")


@pytest.fixture
def agent_h() -> dict[str, str]:
    return _headers(3, "AGENT")


@pytest.fixture
def creer_transformateur(client: TestClient, admin_h: dict) -> Callable[..., dict]:
    def _creer(
        reference: str = "TR-T1",
        etat: str = "BON",
        latitude: float = -19.8659,
        longitude: float = 47.0333,
        actif: bool = True,
        nom: str | None = None,
        puissance: float = 100,
    ) -> dict:
        payload = {
            "reference": reference,
            "nom": nom or f"Poste {reference}",
            "puissance": puissance,
            "etat": etat,
            "latitude": latitude,
            "longitude": longitude,
            "actif": actif,
        }
        r = client.post("/api/transformateurs", json=payload, headers=admin_h)
        assert r.status_code == 201, r.text
        return r.json()

    return _creer


@pytest.fixture
def creer_inspection(client: TestClient, agent_h: dict) -> Callable[..., dict]:
    def _creer(
        transformateur_id: int,
        etat: str = "BON",
        jours: int = 0,
        type: str = "ROUTINE",
        observation: str | None = None,
    ) -> dict:
        payload = {
            "transformateur_id": transformateur_id,
            "date_inspection": (date.today() - timedelta(days=jours)).isoformat(),
            "type": type,
            "etat": etat,
            "observation": observation,
        }
        r = client.post("/api/inspections", json=payload, headers=agent_h)
        assert r.status_code == 201, r.text
        return r.json()

    return _creer


@pytest.fixture
def creer_intervention(client: TestClient, agent_h: dict) -> Callable[..., dict]:
    def _creer(
        transformateur_id: int,
        statut: str = "PLANIFIEE",
        cout: float | None = None,
        decalage_jours: int = 0,
        type: str = "PREVENTIVE",
        description: str | None = None,
    ) -> dict:
        payload = {
            "transformateur_id": transformateur_id,
            "date_intervention": (date.today() + timedelta(days=decalage_jours)).isoformat(),
            "type": type,
            "statut": statut,
            "cout": cout,
            "description": description,
        }
        r = client.post("/api/interventions", json=payload, headers=agent_h)
        assert r.status_code == 201, r.text
        return r.json()

    return _creer