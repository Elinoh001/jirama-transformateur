"""
Données de développement : utilisateurs, transformateurs, inspections, interventions,
relevés de charge et pannes.

Le script est rejouable :
  - utilisateurs et transformateurs : créés seulement s'ils n'existent pas ;
  - inspections, interventions, relevés, pannes : créés seulement si la table est vide.

Les dates sont calculées par rapport à aujourd'hui.

Usage (depuis le dossier backend) :
    python -m scripts.seed_data
"""
import math
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select

from app.config.security import hash_password
from app.database.connection import SessionLocal
from app.models.inspection import EtatHuile, Inspection, StatutInspection
from app.models.intervention import Intervention, StatutIntervention
from app.models.panne import GravitePanne, Panne, StatutPanne, TypePanne
from app.models.releve_charge import ReleveCharge
from app.models.transformateur import EtatTransformateur, NiveauHuile, Transformateur
from app.models.utilisateur import RoleUtilisateur, Utilisateur
from app.services.transformateur_service import build_point, recalculer_prochaine_inspection

# Comptes de DÉVELOPPEMENT uniquement : ne jamais les utiliser en production.
UTILISATEURS_TEST = [
    {"nom": "Admin", "prenom": "Système", "email": "admin@jirama.local",
     "password": "Admin123!", "role": RoleUtilisateur.ADMIN},
    {"nom": "Rakoto", "prenom": "Superviseur", "email": "superviseur@jirama.local",
     "password": "Superviseur123!", "role": RoleUtilisateur.SUPERVISEUR},
    {"nom": "Rabe", "prenom": "Agent", "email": "agent@jirama.local",
     "password": "Agent123!", "role": RoleUtilisateur.AGENT},
]

B = EtatTransformateur.BON
S = EtatTransformateur.A_SURVEILLER
C = EtatTransformateur.CRITIQUE

HM = "Huile minérale (CEI 60296)"
HV = "Huile végétale (ester naturel)"

# Coordonnées fictives mais réalistes, autour d'Antsirabe (centre ≈ -19.866, 47.033).
TRANSFORMATEURS_TEST = [
    {"reference": "TR-001", "nom": "Poste Centre-ville Antsirabe", "secteur": "Centre-ville",
     "puissance": 400, "tension_mt": 20.0, "tension_bt": 400.0, "type_huile": HM,
     "niveau_huile": NiveauHuile.NORMAL, "date_installation": date(2012, 3, 15), "etat": B,
     "periodicite": 12, "latitude": -19.8659, "longitude": 47.0333, "actif": True},
    {"reference": "TR-002", "nom": "Poste Ambalavola", "secteur": "Ambalavola",
     "puissance": 250, "tension_mt": 20.0, "tension_bt": 400.0, "type_huile": HM,
     "niveau_huile": NiveauHuile.NORMAL, "date_installation": date(2015, 7, 2), "etat": B,
     "periodicite": 12, "latitude": -19.8712, "longitude": 47.0401, "actif": True},
    {"reference": "TR-003", "nom": "Poste Antanambao", "secteur": "Antanambao",
     "puissance": 160, "tension_mt": 20.0, "tension_bt": 400.0, "type_huile": HM,
     "niveau_huile": NiveauHuile.NORMAL, "date_installation": date(2008, 11, 20), "etat": S,
     "periodicite": 12, "latitude": -19.8583, "longitude": 47.0276, "actif": True},
    {"reference": "TR-004", "nom": "Poste Mahazoarivo", "secteur": "Mahazoarivo",
     "puissance": 630, "tension_mt": 20.0, "tension_bt": 400.0, "type_huile": HM,
     "niveau_huile": NiveauHuile.BAS, "date_installation": date(2005, 5, 8), "etat": C,
     "periodicite": 6, "latitude": -19.8794, "longitude": 47.0252, "actif": True},
    {"reference": "TR-005", "nom": "Poste Tsarasaotra", "secteur": "Tsarasaotra",
     "puissance": 100, "tension_mt": 20.0, "tension_bt": 400.0, "type_huile": HV,
     "niveau_huile": NiveauHuile.NORMAL, "date_installation": date(2018, 9, 12), "etat": B,
     "periodicite": 12, "latitude": -19.8531, "longitude": 47.0455, "actif": True},
    {"reference": "TR-006", "nom": "Poste Andranomanelatra", "secteur": "Andranomanelatra",
     "puissance": 200, "tension_mt": 20.0, "tension_bt": 400.0, "type_huile": HM,
     "niveau_huile": NiveauHuile.NORMAL, "date_installation": date(2010, 1, 25), "etat": S,
     "periodicite": 12, "latitude": -19.7842, "longitude": 47.0561, "actif": True},
    {"reference": "TR-007", "nom": "Poste Soanindrarina", "secteur": "Soanindrarina",
     "puissance": 315, "tension_mt": 20.0, "tension_bt": 400.0, "type_huile": HM,
     "niveau_huile": NiveauHuile.BAS, "date_installation": date(2003, 6, 30), "etat": C,
     "periodicite": 6, "latitude": -19.8905, "longitude": 47.0498, "actif": True},
    {"reference": "TR-008", "nom": "Poste Ambohimena (hors service)", "secteur": "Ambohimena",
     "puissance": 50, "tension_mt": 20.0, "tension_bt": 400.0, "type_huile": HM,
     "niveau_huile": NiveauHuile.NORMAL, "date_installation": date(1999, 12, 1), "etat": S,
     "periodicite": 12, "latitude": -19.8467, "longitude": 47.0189, "actif": False},
]

R = StatutInspection.REALISEE
PL = StatutInspection.PLANIFIEE
HB = EtatHuile.BONNE
HD = EtatHuile.DEGRADEE
HC = EtatHuile.CONTAMINEE

# (référence, jours avant aujourd'hui [négatif = futur], type, statut, état constaté, état huile,
#  observation, technicien)
INSPECTIONS_TEST = [
    ("TR-001", 30, "ROUTINE", R, B, HB, "Aucune anomalie constatée.", "Rabe Agent"),
    ("TR-002", 400, "ROUTINE", R, B, HB, "Etat général satisfaisant.", "Randria Jean"),
    ("TR-002", 780, "ROUTINE", R, B, HB, "RAS.", "Randria Jean"),
    ("TR-002", -7, "ROUTINE", PL, None, None, "Inspection périodique en retard à effectuer.", "Randria Jean"),
    ("TR-003", 60, "THERMIQUE", R, S, HB, "Echauffement léger détecté sur les bornes MT.", "Rasoa Hery"),
    ("TR-004", 200, "VISUELLE", R, S, HB, "Traces de rouille sur la cuve.", "Rabe Agent"),
    ("TR-004", 90, "THERMIQUE", R, C, HD, "Température d'huile élevée, fuite d'huile suspectée.", "Rasoa Hery"),
    ("TR-004", 20, "POST_INCIDENT", R, C, HD, "Fuite d'huile confirmée, niveau d'huile bas.", "Rabe Agent"),
    ("TR-005", -14, "ROUTINE", PL, None, None, "Première inspection du poste.", "Rabe Agent"),
    ("TR-006", 150, "VISUELLE", R, S, HB, "Isolateurs encrassés, végétation proche du poste.", "Randria Jean"),
    ("TR-007", 100, "ROUTINE", R, S, HB, "Bruit anormal au fonctionnement.", "Rasoa Hery"),
    ("TR-007", 45, "THERMIQUE", R, C, HD, "Surchauffe importante des enroulements.", "Rasoa Hery"),
    ("TR-007", 10, "POST_INCIDENT", R, C, HC, "Déclenchement de la protection, huile dégradée.", "Rabe Agent"),
    ("TR-008", 500, "VISUELLE", R, S, HB, "Poste mis hors service, à réévaluer.", "Randria Jean"),
]

P = StatutIntervention.PLANIFIEE
E = StatutIntervention.EN_COURS
T = StatutIntervention.TERMINEE
A = StatutIntervention.ANNULEE

# (référence, décalage en jours [négatif = passé], type, description, coût en Ar, statut, technicien)
INTERVENTIONS_TEST = [
    ("TR-001", -120, "PREVENTIVE", "Nettoyage et resserrage des connexions.", 350000, T, "Rabe Agent"),
    ("TR-003", 15, "PREVENTIVE", "Contrôle thermique et resserrage des bornes MT.", 450000, P, "Rasoa Hery"),
    ("TR-004", -85, "CORRECTIVE", "Traitement de la rouille et peinture de la cuve.", 1200000, T, "Rabe Agent"),
    ("TR-004", -5, "CORRECTIVE", "Réparation de la fuite d'huile et remise à niveau.", 2500000, E, "Rasoa Hery"),
    ("TR-005", -1, "PREVENTIVE", "Contrôle préventif avant première inspection.", 280000, E, "Rabe Agent"),
    ("TR-006", -30, "PREVENTIVE", "Elagage et nettoyage des isolateurs (annulée : accès impossible).", None, A, "Randria Jean"),
    ("TR-007", -2, "CORRECTIVE", "Diagnostic des enroulements et filtrage de l'huile.", 3200000, E, "Rasoa Hery"),
    ("TR-007", 3, "REMPLACEMENT", "Remplacement du transformateur par une unité neuve de 315 kVA.", 15000000, P, "Rasoa Hery"),
]

# (référence, jours avant aujourd'hui, puissance mesurée en kVA)
RELEVES_TEST = [
    ("TR-001", 60, 310), ("TR-001", 30, 332), ("TR-001", 5, 350),
    ("TR-002", 45, 190), ("TR-002", 10, 205),
    ("TR-003", 40, 150), ("TR-003", 15, 163), ("TR-003", 3, 172),  # dépasse 100 % : surcharge
    ("TR-004", 30, 540), ("TR-004", 8, 610),
    ("TR-005", 20, 55),
    ("TR-006", 25, 168),
    ("TR-007", 12, 340), ("TR-007", 2, 365),  # surcharge
]

TP = TypePanne
G = GravitePanne
SP = StatutPanne

# (référence, type, gravité, statut, description, jours depuis signalement,
#  jours depuis résolution (None si non résolue), actions correctives, signalé par, résolu par)
PANNES_TEST = [
    ("TR-004", TP.FUITE_HUILE, G.CRITIQUE, SP.EN_COURS,
     "Fuite d'huile importante sous la cuve, niveau d'huile bas.", 20, None, None, "Rabe Agent", None),
    ("TR-004", TP.SURCHAUFFE, G.MAJEURE, SP.RESOLUE,
     "Température élevée des radiateurs.", 100, 92,
     "Nettoyage des radiateurs et remplacement du ventilateur.", "Rabe Agent", "Rasoa Hery"),
    ("TR-007", TP.SURCHAUFFE, G.CRITIQUE, SP.SIGNALEE,
     "Surchauffe des enroulements après déclenchement de la protection.", 3, None, None, "Rabe Agent", None),
    ("TR-006", TP.ANOMALIE_MECANIQUE, G.MINEURE, SP.EN_COURS,
     "Vibrations anormales du support.", 9, None, None, "Randria Jean", None),
    ("TR-001", TP.COUPURE, G.MAJEURE, SP.RESOLUE,
     "Coupure générale suite à un défaut sur le départ BT.", 150, 149,
     "Remplacement du fusible et vérification du départ BT.", "Rabe Agent", "Rabe Agent"),
]


def seed_utilisateurs() -> None:
    print("Utilisateurs :")
    with SessionLocal() as db:
        for data in UTILISATEURS_TEST:
            if db.scalar(select(Utilisateur).where(Utilisateur.email == data["email"])):
                print(f"   (déjà présent) {data['email']}")
                continue
            db.add(
                Utilisateur(
                    nom=data["nom"],
                    prenom=data["prenom"],
                    email=data["email"],
                    mot_de_passe=hash_password(data["password"]),
                    role=data["role"],
                    actif=True,
                )
            )
            print(f"   créé : {data['email']} ({data['role'].value})")
        db.commit()


def seed_transformateurs() -> None:
    print("Transformateurs :")
    with SessionLocal() as db:
        for data in TRANSFORMATEURS_TEST:
            if db.scalar(select(Transformateur).where(Transformateur.reference == data["reference"])):
                print(f"   (déjà présent) {data['reference']}")
                continue
            db.add(
                Transformateur(
                    reference=data["reference"],
                    nom=data["nom"],
                    secteur=data["secteur"],
                    puissance=data["puissance"],
                    tension_mt=data["tension_mt"],
                    tension_bt=data["tension_bt"],
                    type_huile=data["type_huile"],
                    niveau_huile=data["niveau_huile"],
                    date_installation=data["date_installation"],
                    etat=data["etat"],
                    periodicite_inspection_mois=data["periodicite"],
                    actif=data["actif"],
                    localisation=build_point(data["latitude"], data["longitude"]),
                )
            )
            print(f"   créé : {data['reference']} ({data['etat'].value}, {data['secteur']})")
        db.commit()


def _transformateurs_par_reference(db) -> dict[str, Transformateur]:
    return {t.reference: t for t in db.scalars(select(Transformateur)).all()}


def seed_inspections() -> None:
    print("Inspections :")
    with SessionLocal() as db:
        nombre = db.scalar(select(func.count()).select_from(Inspection))
        if nombre and nombre > 0:
            print(f"   (déjà présentes : {nombre}) rien à créer")
            return

        par_ref = _transformateurs_par_reference(db)
        aujourdhui = date.today()
        for reference, jours, type_, statut, etat, etat_huile, observation, technicien in INSPECTIONS_TEST:
            db.add(
                Inspection(
                    transformateur_id=par_ref[reference].id,
                    date_inspection=aujourdhui - timedelta(days=jours),
                    type=type_,
                    statut=statut,
                    etat=etat,
                    etat_huile=etat_huile,
                    observation=observation,
                    technicien=technicien,
                )
            )
        db.flush()

        # Prochaine échéance = dernière inspection réalisée + périodicité
        for t in par_ref.values():
            recalculer_prochaine_inspection(db, t)
        db.commit()
        print(f"   {len(INSPECTIONS_TEST)} inspections créées (dont 2 planifiées)")


def seed_interventions() -> None:
    print("Interventions :")
    with SessionLocal() as db:
        nombre = db.scalar(select(func.count()).select_from(Intervention))
        if nombre and nombre > 0:
            print(f"   (déjà présentes : {nombre}) rien à créer")
            return

        par_ref = _transformateurs_par_reference(db)
        aujourdhui = date.today()
        for reference, decalage, type_, description, cout, statut, technicien in INTERVENTIONS_TEST:
            db.add(
                Intervention(
                    transformateur_id=par_ref[reference].id,
                    date_intervention=aujourdhui + timedelta(days=decalage),
                    type=type_,
                    description=description,
                    cout=cout,
                    statut=statut,
                    technicien=technicien,
                )
            )
        db.commit()
        print(f"   {len(INTERVENTIONS_TEST)} interventions créées")


def seed_releves() -> None:
    print("Relevés de charge :")
    with SessionLocal() as db:
        nombre = db.scalar(select(func.count()).select_from(ReleveCharge))
        if nombre and nombre > 0:
            print(f"   (déjà présents : {nombre}) rien à créer")
            return

        par_ref = _transformateurs_par_reference(db)
        aujourdhui = date.today()
        for reference, jours, puissance in RELEVES_TEST:
            t = par_ref[reference]
            # Courant triphasé : I = S / (racine(3) x U)
            courant = round(puissance * 1000 / (math.sqrt(3) * t.tension_bt), 1)
            db.add(
                ReleveCharge(
                    transformateur_id=t.id,
                    date_releve=aujourdhui - timedelta(days=jours),
                    puissance_mesuree=puissance,
                    courant_mesure=courant,
                    taux_charge=round(puissance / t.puissance * 100, 2),
                    releve_par="Rabe Agent",
                )
            )
        db.commit()
        print(f"   {len(RELEVES_TEST)} relevés créés")


def seed_pannes() -> None:
    print("Pannes :")
    with SessionLocal() as db:
        nombre = db.scalar(select(func.count()).select_from(Panne))
        if nombre and nombre > 0:
            print(f"   (déjà présentes : {nombre}) rien à créer")
            return

        par_ref = _transformateurs_par_reference(db)
        maintenant = datetime.now(timezone.utc)
        for (reference, type_panne, gravite, statut, description, jours_signal,
             jours_resolution, actions, signale_par, resolu_par) in PANNES_TEST:
            db.add(
                Panne(
                    transformateur_id=par_ref[reference].id,
                    type_panne=type_panne,
                    gravite=gravite,
                    statut=statut,
                    description=description,
                    signale_par=signale_par,
                    date_signalement=maintenant - timedelta(days=jours_signal),
                    date_resolution=(
                        maintenant - timedelta(days=jours_resolution)
                        if jours_resolution is not None
                        else None
                    ),
                    actions_correctives=actions,
                    resolu_par=resolu_par,
                )
            )
        db.commit()
        print(f"   {len(PANNES_TEST)} pannes créées (dont 3 actives)")


def main() -> None:
    seed_utilisateurs()
    seed_transformateurs()
    seed_inspections()
    seed_interventions()
    seed_releves()
    seed_pannes()
    print("Terminé.")


if __name__ == "__main__":
    main()