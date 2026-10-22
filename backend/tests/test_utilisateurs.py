NOUVEAU = {
    "nom": "Nouveau",
    "prenom": "Utilisateur",
    "email": "nouveau@jirama.local",
    "mot_de_passe": "Nouveau123!",
    "role": "AGENT",
}


def test_admin_cree_un_utilisateur(client, admin_h):
    r = client.post("/api/utilisateurs", json=NOUVEAU, headers=admin_h)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "nouveau@jirama.local"
    assert data["role"] == "AGENT"
    assert "mot_de_passe" not in data


def test_nouvel_utilisateur_peut_se_connecter(client, admin_h):
    client.post("/api/utilisateurs", json=NOUVEAU, headers=admin_h)
    r = client.post(
        "/api/auth/login", json={"email": "nouveau@jirama.local", "password": "Nouveau123!"}
    )
    assert r.status_code == 200


def test_email_en_double_409(client, admin_h):
    client.post("/api/utilisateurs", json=NOUVEAU, headers=admin_h)
    r = client.post("/api/utilisateurs", json=NOUVEAU, headers=admin_h)
    assert r.status_code == 409


def test_mot_de_passe_trop_court_422(client, admin_h):
    r = client.post("/api/utilisateurs", json={**NOUVEAU, "mot_de_passe": "court"}, headers=admin_h)
    assert r.status_code == 422


def test_role_invalide_422(client, admin_h):
    r = client.post("/api/utilisateurs", json={**NOUVEAU, "role": "ROOT"}, headers=admin_h)
    assert r.status_code == 422


def test_liste_et_detail(client, admin_h):
    liste = client.get("/api/utilisateurs", headers=admin_h)
    assert liste.status_code == 200
    assert len(liste.json()) == 3
    assert client.get("/api/utilisateurs/2", headers=admin_h).json()["role"] == "SUPERVISEUR"
    assert client.get("/api/utilisateurs/999", headers=admin_h).status_code == 404


def test_changement_de_role(client, admin_h):
    r = client.put("/api/utilisateurs/3", json={"role": "SUPERVISEUR"}, headers=admin_h)
    assert r.status_code == 200
    assert r.json()["role"] == "SUPERVISEUR"


def test_changement_de_mot_de_passe(client, admin_h):
    client.put("/api/utilisateurs/3", json={"mot_de_passe": "NouveauMdp123!"}, headers=admin_h)
    ancien = client.post("/api/auth/login", json={"email": "agent@jirama.local", "password": "Test1234!"})
    nouveau = client.post("/api/auth/login", json={"email": "agent@jirama.local", "password": "NouveauMdp123!"})
    assert ancien.status_code == 401
    assert nouveau.status_code == 200


def test_modification_sans_mot_de_passe_conserve_l_ancien(client, admin_h):
    client.put("/api/utilisateurs/3", json={"nom": "Autre"}, headers=admin_h)
    r = client.post("/api/auth/login", json={"email": "agent@jirama.local", "password": "Test1234!"})
    assert r.status_code == 200


def test_admin_ne_peut_pas_se_supprimer_ni_se_desactiver_ni_changer_son_role(client, admin_h):
    assert client.delete("/api/utilisateurs/1", headers=admin_h).status_code == 400
    assert client.put("/api/utilisateurs/1", json={"actif": False}, headers=admin_h).status_code == 400
    assert client.put("/api/utilisateurs/1", json={"role": "AGENT"}, headers=admin_h).status_code == 400


def test_suppression_d_un_autre_utilisateur(client, admin_h):
    assert client.delete("/api/utilisateurs/3", headers=admin_h).status_code == 204
    assert client.get("/api/utilisateurs/3", headers=admin_h).status_code == 404


def test_superviseur_et_agent_refuses_partout(client, sup_h, agent_h):
    for headers in (sup_h, agent_h):
        assert client.get("/api/utilisateurs", headers=headers).status_code == 403
        assert client.get("/api/utilisateurs/1", headers=headers).status_code == 403
        assert client.post("/api/utilisateurs", json=NOUVEAU, headers=headers).status_code == 403
        assert client.put("/api/utilisateurs/3", json={"nom": "X"}, headers=headers).status_code == 403
        assert client.delete("/api/utilisateurs/3", headers=headers).status_code == 403


def test_sans_token_401(client):
    assert client.get("/api/utilisateurs").status_code == 401