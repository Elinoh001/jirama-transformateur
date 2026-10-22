from datetime import datetime, timedelta, timezone

import jwt
import pytest
from sqlalchemy import select, update

from app.config.settings import settings
from app.models.utilisateur import RoleUtilisateur, Utilisateur

PASSWORD = "Test1234!"


def login(client, email: str, password: str = PASSWORD):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"
    assert body["postgis"].startswith("3.")


@pytest.mark.parametrize(
    "email,role",
    [
        ("admin@jirama.local", "ADMIN"),
        ("superviseur@jirama.local", "SUPERVISEUR"),
        ("agent@jirama.local", "AGENT"),
    ],
)
def test_login_ok_pour_les_3_roles(client, email, role):
    r = login(client, email)
    assert r.status_code == 200
    data = r.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["role"] == role
    assert "mot_de_passe" not in data["user"]


def test_login_email_insensible_a_la_casse(client):
    assert login(client, "ADMIN@JIRAMA.LOCAL").status_code == 200


def test_login_mauvais_mot_de_passe(client):
    r = login(client, "admin@jirama.local", "mauvais")
    assert r.status_code == 401


def test_login_email_inconnu_meme_message_que_mauvais_mdp(client):
    inconnu = login(client, "inconnu@jirama.local")
    mauvais = login(client, "admin@jirama.local", "mauvais")
    assert inconnu.status_code == mauvais.status_code == 401
    assert inconnu.json()["detail"] == mauvais.json()["detail"]


def test_login_compte_desactive(client, db):
    db.execute(update(Utilisateur).where(Utilisateur.email == "agent@jirama.local").values(actif=False))
    db.commit()
    assert login(client, "agent@jirama.local").status_code == 403


def test_mot_de_passe_hashe_en_base(db):
    hashes = db.scalars(select(Utilisateur.mot_de_passe)).all()
    assert len(hashes) == 3
    for h in hashes:
        assert h.startswith("$2b$")
        assert h != PASSWORD


def test_me_avec_token(client):
    token = login(client, "agent@jirama.local").json()["access_token"]
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "agent@jirama.local"
    assert r.json()["role"] == "AGENT"
    assert "mot_de_passe" not in r.json()


def test_me_sans_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_faux_token(client):
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer faux.token.ici"})
    assert r.status_code == 401


def test_token_expire(client):
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode({"sub": "1", "role": "ADMIN", "exp": expire}, settings.SECRET_KEY, algorithm="HS256")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_token_signe_avec_une_autre_cle(client):
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    token = jwt.encode({"sub": "1", "role": "ADMIN", "exp": expire}, "une-autre-cle-secrete-assez-longue-123", algorithm="HS256")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_utilisateur_desactive_avec_token_valide_est_refuse(client, db, agent_h):
    db.execute(update(Utilisateur).where(Utilisateur.email == "agent@jirama.local").values(actif=False))
    db.commit()
    assert client.get("/api/auth/me", headers=agent_h).status_code == 401


def test_le_role_est_lu_en_base_et_non_dans_le_token(client, db, agent_h):
    # Le token dit AGENT : accès refusé à la gestion des utilisateurs.
    assert client.get("/api/utilisateurs", headers=agent_h).status_code == 403

    # Promotion en base : le MÊME token donne maintenant accès (le rôle vient de la base).
    db.execute(
        update(Utilisateur)
        .where(Utilisateur.email == "agent@jirama.local")
        .values(role=RoleUtilisateur.ADMIN)
    )
    db.commit()
    assert client.get("/api/utilisateurs", headers=agent_h).status_code == 200


def test_cors_origine_autorisee(client):
    r = client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization",
        },
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_origine_inconnue_refusee(client):
    r = client.options(
        "/api/auth/login",
        headers={"Origin": "http://site-malveillant.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in r.headers