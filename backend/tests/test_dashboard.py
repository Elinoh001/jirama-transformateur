from datetime import date


def preparer_donnees(creer_transformateur, creer_inspection, creer_intervention):
    t1 = creer_transformateur(reference="TR-1", etat="BON")  # actif
    t2 = creer_transformateur(reference="TR-2", etat="CRITIQUE")  # actif
    creer_transformateur(reference="TR-3", etat="A_SURVEILLER", actif=False)  # inactif

    creer_inspection(t1["id"], etat="BON")  # t1 -> NORMAL
    creer_intervention(t1["id"], statut="PLANIFIEE")
    creer_intervention(t2["id"], statut="TERMINEE", cout=1000)


def test_statistiques(client, admin_h, creer_transformateur, creer_inspection, creer_intervention):
    preparer_donnees(creer_transformateur, creer_inspection, creer_intervention)

    r = client.get("/api/dashboard/statistics", headers=admin_h)
    assert r.status_code == 200
    s = r.json()

    assert s["total_transformateurs"] == 3
    assert s["transformateurs_actifs"] == 2
    assert s["transformateurs_inactifs"] == 1
    assert s["transformateurs_bon"] == 1
    assert s["transformateurs_a_surveiller"] == 1
    assert s["transformateurs_critiques"] == 1

    assert s["total_inspections"] == 1
    assert s["total_interventions"] == 2
    assert s["interventions_planifiees"] == 1
    assert s["interventions_en_cours"] == 0
    assert s["interventions_terminees"] == 1
    assert s["interventions_annulees"] == 0
    assert s["cout_total_interventions_terminees"] == 1000

    # priorités : transformateurs ACTIFS uniquement (TR-1 normal, TR-2 prioritaire)
    assert s["nb_priorites"] == 1
    assert s["repartition_priorites"] == {"normal": 1, "a_surveiller": 0, "prioritaire": 1}


def test_activite_mensuelle(client, admin_h, creer_transformateur, creer_inspection, creer_intervention):
    preparer_donnees(creer_transformateur, creer_inspection, creer_intervention)
    activite = client.get("/api/dashboard/statistics", headers=admin_h).json()["activite_mensuelle"]

    assert len(activite) == 6
    mois = [a["mois"] for a in activite]
    assert mois == sorted(mois)

    courant = activite[-1]
    aujourdhui = date.today()
    assert courant["mois"] == f"{aujourdhui.year}-{aujourdhui.month:02d}"
    assert courant["inspections"] == 1
    assert courant["interventions"] == 2


def test_statistiques_sur_base_vide(client, admin_h):
    s = client.get("/api/dashboard/statistics", headers=admin_h).json()
    assert s["total_transformateurs"] == 0
    assert s["nb_priorites"] == 0
    assert s["cout_total_interventions_terminees"] == 0
    assert len(s["activite_mensuelle"]) == 6


def test_permissions_statistiques(client, admin_h, sup_h, agent_h):
    assert client.get("/api/dashboard/statistics", headers=admin_h).status_code == 200
    assert client.get("/api/dashboard/statistics", headers=sup_h).status_code == 200
    assert client.get("/api/dashboard/statistics", headers=agent_h).status_code == 403
    assert client.get("/api/dashboard/statistics").status_code == 401


def test_priorites_du_dashboard(client, admin_h, creer_transformateur, creer_inspection, creer_intervention):
    preparer_donnees(creer_transformateur, creer_inspection, creer_intervention)

    defaut = client.get("/api/dashboard/priorities", headers=admin_h).json()
    assert [p["reference"] for p in defaut] == ["TR-2"]  # NORMAL et inactifs exclus

    avec_normal = client.get("/api/dashboard/priorities?inclure_normal=true", headers=admin_h).json()
    assert [p["reference"] for p in avec_normal] == ["TR-2", "TR-1"]

    seulement_normal = client.get("/api/dashboard/priorities?niveau=NORMAL", headers=admin_h).json()
    assert [p["reference"] for p in seulement_normal] == ["TR-1"]

    limite = client.get("/api/dashboard/priorities?inclure_normal=true&limit=1", headers=admin_h).json()
    assert len(limite) == 1


def test_priorites_validation_et_permissions(client, admin_h, sup_h, agent_h):
    assert client.get("/api/dashboard/priorities?limit=0", headers=admin_h).status_code == 422
    assert client.get("/api/dashboard/priorities?niveau=XXX", headers=admin_h).status_code == 422
    for headers in (admin_h, sup_h, agent_h):
        assert client.get("/api/dashboard/priorities", headers=headers).status_code == 200
    assert client.get("/api/dashboard/priorities").status_code == 401