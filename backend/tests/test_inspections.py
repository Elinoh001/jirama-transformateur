from datetime import date, timedelta


def payload(transformateur_id: int, **extra) -> dict:
    base = {
        "transformateur_id": transformateur_id,
        "date_inspection": date.today().isoformat(),
        "type": "ROUTINE",
        "etat": "BON",
        "observation": "RAS",
    }
    base.update(extra)
    return base


def test_agent_cree_une_inspection_technicien_et_type_automatiques(client, agent_h, creer_transformateur):
    t = creer_transformateur()
    r = client.post("/api/inspections", json=payload(t["id"], type="visuelle"), headers=agent_h)
    assert r.status_code == 201
    data = r.json()
    assert data["type"] == "VISUELLE"  # normalisé en majuscules
    assert data["technicien"] == "Agent Test"  # nom de l'utilisateur connecté
    assert data["transformateur_reference"] == t["reference"]
    assert data["transformateur_nom"] == t["nom"]


def test_technicien_fourni_est_conserve(client, admin_h, creer_transformateur):
    t = creer_transformateur()
    r = client.post("/api/inspections", json=payload(t["id"], technicien="Rasoa Hery"), headers=admin_h)
    assert r.status_code == 201
    assert r.json()["technicien"] == "Rasoa Hery"


def test_modification_d_une_inspection(client, agent_h, creer_transformateur, creer_inspection):
    t = creer_transformateur()
    i = creer_inspection(t["id"])
    r = client.put(
        f"/api/inspections/{i['id']}",
        json={"etat": "A_SURVEILLER", "observation": "Echauffement"},
        headers=agent_h,
    )
    assert r.status_code == 200
    assert r.json()["etat"] == "A_SURVEILLER"
    assert r.json()["observation"] == "Echauffement"


def test_le_transformateur_d_une_inspection_ne_change_pas(client, agent_h, creer_transformateur, creer_inspection):
    a = creer_transformateur(reference="TR-A")
    b = creer_transformateur(reference="TR-B")
    i = creer_inspection(a["id"])
    client.put(f"/api/inspections/{i['id']}", json={"transformateur_id": b["id"]}, headers=agent_h)
    lu = client.get(f"/api/inspections/{i['id']}", headers=agent_h).json()
    assert lu["transformateur_id"] == a["id"]


def test_filtres(client, admin_h, creer_transformateur, creer_inspection):
    a = creer_transformateur(reference="TR-A")
    b = creer_transformateur(reference="TR-B")
    creer_inspection(a["id"], etat="BON")
    creer_inspection(a["id"], etat="CRITIQUE", jours=5)
    creer_inspection(b["id"], etat="CRITIQUE", jours=10)

    assert len(client.get("/api/inspections", headers=admin_h).json()) == 3
    assert len(client.get(f"/api/inspections?transformateur_id={a['id']}", headers=admin_h).json()) == 2
    assert len(client.get("/api/inspections?etat=CRITIQUE", headers=admin_h).json()) == 2


def test_tri_de_la_plus_recente_a_la_plus_ancienne(client, admin_h, creer_transformateur, creer_inspection):
    t = creer_transformateur()
    creer_inspection(t["id"], jours=30)
    creer_inspection(t["id"], jours=1)
    creer_inspection(t["id"], jours=10)
    dates = [i["date_inspection"] for i in client.get("/api/inspections", headers=admin_h).json()]
    assert dates == sorted(dates, reverse=True)


def test_erreurs_de_validation(client, admin_h, creer_transformateur):
    t = creer_transformateur()
    demain = (date.today() + timedelta(days=1)).isoformat()

    assert client.post("/api/inspections", json=payload(999), headers=admin_h).status_code == 404
    assert client.post("/api/inspections", json=payload(t["id"], type="INCONNU"), headers=admin_h).status_code == 422
    assert client.post("/api/inspections", json=payload(t["id"], etat="EXCELLENT"), headers=admin_h).status_code == 422
    assert client.post("/api/inspections", json=payload(t["id"], date_inspection=demain), headers=admin_h).status_code == 422


def test_inexistante_404(client, admin_h):
    assert client.get("/api/inspections/9999", headers=admin_h).status_code == 404
    assert client.put("/api/inspections/9999", json={"etat": "BON"}, headers=admin_h).status_code == 404


def test_superviseur_consulte_mais_n_ecrit_pas(client, sup_h, creer_transformateur, creer_inspection):
    t = creer_transformateur()
    i = creer_inspection(t["id"])
    assert client.get("/api/inspections", headers=sup_h).status_code == 200
    assert client.get(f"/api/inspections/{i['id']}", headers=sup_h).status_code == 200
    assert client.post("/api/inspections", json=payload(t["id"]), headers=sup_h).status_code == 403
    assert client.put(f"/api/inspections/{i['id']}", json={"etat": "BON"}, headers=sup_h).status_code == 403


def test_sans_token_401(client):
    assert client.get("/api/inspections").status_code == 401
    assert client.post("/api/inspections", json={}).status_code == 401