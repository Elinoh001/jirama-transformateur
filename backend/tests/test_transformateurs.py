import pytest
from sqlalchemy import text


# ---------------------------------------------------------------- PostGIS


def test_la_colonne_localisation_est_un_point_srid_4326(db):
    ligne = db.execute(
        text(
            "SELECT srid, type FROM geometry_columns "
            "WHERE f_table_name = 'transformateurs' AND f_geometry_column = 'localisation'"
        )
    ).one()
    assert ligne.srid == 4326
    assert ligne.type == "POINT"


def test_geometrie_enregistree_et_relue_POINT_SRID_4326(client, db, admin_h, creer_transformateur):
    t = creer_transformateur(reference="TR-GIS", latitude=-19.8659, longitude=47.0333)

    # 1) Ce qui est stocké dans PostGIS
    ligne = db.execute(
        text(
            "SELECT ST_SRID(localisation) AS srid, GeometryType(localisation) AS type, "
            "ST_X(localisation) AS x, ST_Y(localisation) AS y "
            "FROM transformateurs WHERE id = :id"
        ),
        {"id": t["id"]},
    ).one()
    assert ligne.srid == 4326
    assert ligne.type == "POINT"
    assert ligne.x == pytest.approx(47.0333, abs=1e-6)  # X = longitude
    assert ligne.y == pytest.approx(-19.8659, abs=1e-6)  # Y = latitude

    # 2) Ce que l'API renvoie à Leaflet
    lu = client.get(f"/api/transformateurs/{t['id']}", headers=admin_h).json()
    assert lu["latitude"] == pytest.approx(-19.8659, abs=1e-6)
    assert lu["longitude"] == pytest.approx(47.0333, abs=1e-6)


def test_modification_des_coordonnees_met_a_jour_la_geometrie(client, db, admin_h, creer_transformateur):
    t = creer_transformateur()
    r = client.put(
        f"/api/transformateurs/{t['id']}",
        json={"latitude": -19.9, "longitude": 47.1},
        headers=admin_h,
    )
    assert r.status_code == 200
    ligne = db.execute(
        text("SELECT ST_X(localisation) AS x, ST_Y(localisation) AS y FROM transformateurs WHERE id = :id"),
        {"id": t["id"]},
    ).one()
    assert ligne.x == pytest.approx(47.1, abs=1e-6)
    assert ligne.y == pytest.approx(-19.9, abs=1e-6)


def test_recherche_spatiale_native_ST_DWithin(db, creer_transformateur):
    creer_transformateur(reference="TR-PROCHE", latitude=-19.8659, longitude=47.0333)
    creer_transformateur(reference="TR-LOIN", latitude=-18.9, longitude=47.5)
    refs = db.scalars(
        text(
            "SELECT reference FROM transformateurs "
            "WHERE ST_DWithin(localisation::geography, "
            "ST_SetSRID(ST_MakePoint(47.0333, -19.8659), 4326)::geography, 3000)"
        )
    ).all()
    assert refs == ["TR-PROCHE"]


# ---------------------------------------------------------------- CRUD


def test_cycle_complet_creation_lecture_modification_suppression(client, admin_h, creer_transformateur):
    t = creer_transformateur(reference="TR-CRUD")
    assert t["id"] > 0
    assert t["etat"] == "BON"

    lu = client.get(f"/api/transformateurs/{t['id']}", headers=admin_h)
    assert lu.status_code == 200
    assert lu.json()["reference"] == "TR-CRUD"

    modif = client.put(
        f"/api/transformateurs/{t['id']}", json={"etat": "A_SURVEILLER", "nom": "Nouveau nom"}, headers=admin_h
    )
    assert modif.status_code == 200
    assert modif.json()["etat"] == "A_SURVEILLER"
    assert modif.json()["nom"] == "Nouveau nom"

    assert client.delete(f"/api/transformateurs/{t['id']}", headers=admin_h).status_code == 204
    assert client.get(f"/api/transformateurs/{t['id']}", headers=admin_h).status_code == 404


def test_reference_en_double_409(client, admin_h, creer_transformateur):
    creer_transformateur(reference="TR-DUP")
    r = client.post(
        "/api/transformateurs",
        json={"reference": "TR-DUP", "nom": "Doublon", "puissance": 50, "latitude": -19.8, "longitude": 47.0},
        headers=admin_h,
    )
    assert r.status_code == 409


def test_modification_vers_une_reference_existante_409(client, admin_h, creer_transformateur):
    creer_transformateur(reference="TR-A")
    b = creer_transformateur(reference="TR-B")
    r = client.put(f"/api/transformateurs/{b['id']}", json={"reference": "TR-A"}, headers=admin_h)
    assert r.status_code == 409


@pytest.mark.parametrize(
    "champ,valeur",
    [("latitude", 200), ("latitude", -91), ("longitude", 181), ("puissance", 0), ("puissance", -5), ("etat", "EXCELLENT")],
)
def test_valeurs_invalides_422(client, admin_h, champ, valeur):
    payload = {"reference": "TR-X", "nom": "Invalide", "puissance": 100, "latitude": -19.8, "longitude": 47.0}
    payload[champ] = valeur
    assert client.post("/api/transformateurs", json=payload, headers=admin_h).status_code == 422


def test_latitude_sans_longitude_422(client, admin_h, creer_transformateur):
    t = creer_transformateur()
    r = client.put(f"/api/transformateurs/{t['id']}", json={"latitude": -19.8}, headers=admin_h)
    assert r.status_code == 422


def test_inexistant_404(client, admin_h):
    assert client.get("/api/transformateurs/999", headers=admin_h).status_code == 404
    assert client.put("/api/transformateurs/999", json={"nom": "X"}, headers=admin_h).status_code == 404
    assert client.delete("/api/transformateurs/999", headers=admin_h).status_code == 404


def test_suppression_en_cascade(client, db, admin_h, creer_transformateur, creer_inspection, creer_intervention):
    t = creer_transformateur()
    creer_inspection(t["id"])
    creer_intervention(t["id"])
    client.delete(f"/api/transformateurs/{t['id']}", headers=admin_h)
    assert db.scalar(text("SELECT COUNT(*) FROM inspections")) == 0
    assert db.scalar(text("SELECT COUNT(*) FROM interventions")) == 0


# ---------------------------------------------------------------- recherche et filtres


def test_recherche_et_filtres(client, admin_h, creer_transformateur):
    creer_transformateur(reference="TR-001", nom="Poste Centre", etat="BON")
    creer_transformateur(reference="TR-002", nom="Poste Ambalavola", etat="CRITIQUE")
    creer_transformateur(reference="TR-003", nom="Poste Nord", etat="BON", actif=False)

    def refs(url):
        r = client.get(url, headers=admin_h)
        assert r.status_code == 200
        return sorted(t["reference"] for t in r.json())

    assert refs("/api/transformateurs") == ["TR-001", "TR-002", "TR-003"]
    assert refs("/api/transformateurs?search=TR-001") == ["TR-001"]
    assert refs("/api/transformateurs?search=ambalavola") == ["TR-002"]  # insensible à la casse
    assert refs("/api/transformateurs?search=poste") == ["TR-001", "TR-002", "TR-003"]
    assert refs("/api/transformateurs?search=introuvable") == []
    assert refs("/api/transformateurs?etat=CRITIQUE") == ["TR-002"]
    assert refs("/api/transformateurs?actif=false") == ["TR-003"]
    assert refs("/api/transformateurs?actif=true") == ["TR-001", "TR-002"]


def test_la_liste_contient_la_priorite(client, admin_h, creer_transformateur):
    creer_transformateur(reference="TR-001")
    t = client.get("/api/transformateurs", headers=admin_h).json()[0]
    assert t["priorite"] in {"NORMAL", "A_SURVEILLER", "PRIORITAIRE"}
    assert isinstance(t["priorite_motifs"], list) and t["priorite_motifs"]


# ---------------------------------------------------------------- permissions


def test_permissions_ecriture_reservee_a_admin(client, sup_h, agent_h, admin_h, creer_transformateur):
    t = creer_transformateur(reference="TR-PERM")
    payload = {"reference": "TR-N", "nom": "N", "puissance": 10, "latitude": -19.8, "longitude": 47.0}

    for headers in (sup_h, agent_h):
        assert client.post("/api/transformateurs", json=payload, headers=headers).status_code == 403
        assert client.put(f"/api/transformateurs/{t['id']}", json={"nom": "X"}, headers=headers).status_code == 403
        assert client.delete(f"/api/transformateurs/{t['id']}", headers=headers).status_code == 403

    # rien n'a été modifié ni supprimé
    assert client.get(f"/api/transformateurs/{t['id']}", headers=admin_h).json()["nom"] == t["nom"]


def test_lecture_autorisee_aux_3_roles_et_refusee_sans_token(client, admin_h, sup_h, agent_h):
    for headers in (admin_h, sup_h, agent_h):
        assert client.get("/api/transformateurs", headers=headers).status_code == 200
    assert client.get("/api/transformateurs").status_code == 401
    assert client.get("/api/transformateurs/priorites").status_code == 401