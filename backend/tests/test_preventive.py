"""
Suivi préventif : règles (tests unitaires, sans base) puis comportement via l'API.
"""
from datetime import date, timedelta
from types import SimpleNamespace

from app.models.transformateur import EtatTransformateur as E
from app.services.preventive_service import NiveauPriorite as N
from app.services.preventive_service import calculer_priorite

AUJOURDHUI = date(2026, 10, 9)  # date fixe : tests déterministes


def insp(jours: int, etat: E, id: int = 0):
    return SimpleNamespace(id=id, date_inspection=AUJOURDHUI - timedelta(days=jours), etat=etat)


# ---------------------------------------------------------------- règles NORMAL


def test_bon_et_inspection_recente_est_normal():
    r = calculer_priorite(E.BON, [insp(30, E.BON)], AUJOURDHUI)
    assert r.niveau == N.NORMAL
    assert r.motifs == ["Etat BON et inspection récente"]
    assert r.jours_depuis_derniere_inspection == 30


# ---------------------------------------------------------------- règles A_SURVEILLER


def test_etat_a_surveiller():
    assert calculer_priorite(E.A_SURVEILLER, [insp(10, E.BON)], AUJOURDHUI).niveau == N.A_SURVEILLER


def test_derniere_inspection_a_surveiller():
    assert calculer_priorite(E.BON, [insp(10, E.A_SURVEILLER)], AUJOURDHUI).niveau == N.A_SURVEILLER


def test_aucune_inspection():
    r = calculer_priorite(E.BON, [], AUJOURDHUI)
    assert r.niveau == N.A_SURVEILLER
    assert "Aucune inspection enregistrée" in r.motifs
    assert r.derniere_inspection is None
    assert r.jours_depuis_derniere_inspection is None


def test_seuil_inspection_ancienne_365_jours():
    assert calculer_priorite(E.BON, [insp(365, E.BON)], AUJOURDHUI).niveau == N.NORMAL  # pile au seuil
    assert calculer_priorite(E.BON, [insp(366, E.BON)], AUJOURDHUI).niveau == N.A_SURVEILLER


# ---------------------------------------------------------------- règles PRIORITAIRE


def test_etat_critique():
    assert calculer_priorite(E.CRITIQUE, [insp(10, E.BON)], AUJOURDHUI).niveau == N.PRIORITAIRE


def test_derniere_inspection_critique_meme_si_transformateur_bon():
    assert calculer_priorite(E.BON, [insp(5, E.CRITIQUE)], AUJOURDHUI).niveau == N.PRIORITAIRE


def test_deux_anomalies_critiques_dans_la_fenetre_de_180_jours():
    inspections = [insp(100, E.CRITIQUE, 1), insp(50, E.CRITIQUE, 2), insp(10, E.BON, 3)]
    r = calculer_priorite(E.BON, inspections, AUJOURDHUI)
    assert r.niveau == N.PRIORITAIRE
    assert r.nb_anomalies_critiques_recentes == 2


def test_une_anomalie_critique_hors_fenetre_ne_compte_pas():
    inspections = [insp(200, E.CRITIQUE, 1), insp(50, E.CRITIQUE, 2), insp(10, E.BON, 3)]
    r = calculer_priorite(E.BON, inspections, AUJOURDHUI)
    assert r.nb_anomalies_critiques_recentes == 1
    assert r.niveau == N.NORMAL


def test_le_niveau_le_plus_grave_l_emporte():
    r = calculer_priorite(E.A_SURVEILLER, [insp(5, E.CRITIQUE)], AUJOURDHUI)
    assert r.niveau == N.PRIORITAIRE
    # les motifs des deux niveaux sont conservés, les plus graves d'abord
    assert r.motifs[0].startswith("Dernière inspection : état CRITIQUE")
    assert any("A SURVEILLER" in m for m in r.motifs)


def test_l_ordre_de_la_liste_n_a_pas_d_importance():
    a = [insp(100, E.CRITIQUE, 1), insp(10, E.BON, 2), insp(50, E.CRITIQUE, 3)]
    b = list(reversed(a))
    assert calculer_priorite(E.BON, a, AUJOURDHUI).niveau == calculer_priorite(E.BON, b, AUJOURDHUI).niveau


# ---------------------------------------------------------------- via l'API


def test_la_priorite_reagit_aux_inspections(client, admin_h, creer_transformateur, creer_inspection):
    t = creer_transformateur(etat="BON")
    url = f"/api/transformateurs/{t['id']}"

    assert client.get(url, headers=admin_h).json()["priorite"] == "A_SURVEILLER"  # jamais inspecté

    creer_inspection(t["id"], etat="BON")
    assert client.get(url, headers=admin_h).json()["priorite"] == "NORMAL"

    creer_inspection(t["id"], etat="CRITIQUE")
    lu = client.get(url, headers=admin_h).json()
    assert lu["priorite"] == "PRIORITAIRE"
    assert lu["priorite_motifs"]


def test_liste_des_priorites_tri_et_filtres(client, admin_h, creer_transformateur, creer_inspection):
    t1 = creer_transformateur(reference="TR-1", etat="BON")
    creer_inspection(t1["id"], etat="BON")  # NORMAL
    creer_transformateur(reference="TR-2", etat="CRITIQUE")  # PRIORITAIRE
    creer_transformateur(reference="TR-3", etat="A_SURVEILLER")  # A_SURVEILLER
    creer_transformateur(reference="TR-4", etat="BON", actif=False)  # inactif

    lignes = client.get("/api/transformateurs/priorites", headers=admin_h).json()
    assert [l["reference"] for l in lignes] == ["TR-2", "TR-3", "TR-1"]  # urgent -> normal, sans l'inactif
    assert [l["niveau"] for l in lignes] == ["PRIORITAIRE", "A_SURVEILLER", "NORMAL"]

    assert len(client.get("/api/transformateurs/priorites?inclure_inactifs=true", headers=admin_h).json()) == 4
    seuls = client.get("/api/transformateurs/priorites?niveau=PRIORITAIRE", headers=admin_h).json()
    assert [l["reference"] for l in seuls] == ["TR-2"]
    assert client.get("/api/transformateurs/priorites?niveau=XXX", headers=admin_h).status_code == 422


def test_priorites_accessibles_aux_3_roles(client, admin_h, sup_h, agent_h):
    for headers in (admin_h, sup_h, agent_h):
        assert client.get("/api/transformateurs/priorites", headers=headers).status_code == 200


# ---------------------------------------------------------------- historique


def test_historique_chronologique(client, sup_h, creer_transformateur, creer_inspection, creer_intervention):
    t = creer_transformateur()
    creer_inspection(t["id"], jours=20, etat="BON")
    creer_inspection(t["id"], jours=10, etat="CRITIQUE")
    creer_intervention(t["id"], decalage_jours=-5, statut="EN_COURS", cout=1000)

    h = client.get(f"/api/transformateurs/{t['id']}/historique", headers=sup_h).json()
    assert h["total"] == 3
    assert h["transformateur"]["reference"] == t["reference"]
    assert h["transformateur"]["priorite"] == "PRIORITAIRE"
    assert [e["evenement"] for e in h["evenements"]] == ["INTERVENTION", "INSPECTION", "INSPECTION"]
    assert h["evenements"][0]["statut"] == "EN_COURS"
    assert h["evenements"][0]["cout"] == 1000
    assert h["evenements"][1]["etat"] == "CRITIQUE"

    asc = client.get(f"/api/transformateurs/{t['id']}/historique?ordre=asc", headers=sup_h).json()
    assert [e["evenement"] for e in asc["evenements"]] == ["INSPECTION", "INSPECTION", "INTERVENTION"]


def test_historique_vide(client, admin_h, creer_transformateur):
    t = creer_transformateur()
    h = client.get(f"/api/transformateurs/{t['id']}/historique", headers=admin_h).json()
    assert h["total"] == 0
    assert h["evenements"] == []


def test_historique_erreurs(client, admin_h, creer_transformateur):
    t = creer_transformateur()
    assert client.get("/api/transformateurs/999/historique", headers=admin_h).status_code == 404
    assert client.get(f"/api/transformateurs/{t['id']}/historique").status_code == 401
    assert client.get(f"/api/transformateurs/{t['id']}/historique?ordre=xxx", headers=admin_h).status_code == 422