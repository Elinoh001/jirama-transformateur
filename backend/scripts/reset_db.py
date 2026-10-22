"""
Remet la base de DÉVELOPPEMENT à zéro : supprime les tables du projet, les recrée
avec le schéma actuel, puis recharge les données de test.

À utiliser quand les modèles changent (create_all n'ajoute pas de colonnes à une table existante).
Arrêter le backend (uvicorn) avant de lancer ce script.

Usage (depuis le dossier backend) :
    python -m scripts.reset_db
"""
from sqlalchemy import text

import app.models  # noqa: F401  (enregistre les modèles dans Base.metadata)
from app.database.base import Base
from app.database.connection import engine
from scripts import seed_data


def main() -> None:
    nom_base = engine.url.database
    print(f"ATTENTION : toutes les données de la base '{nom_base}' vont être supprimées.")
    if input(f"Tape le nom de la base ({nom_base}) pour confirmer : ").strip() != nom_base:
        print("Annulé. Rien n'a été modifié.")
        return

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

    print("Suppression des tables...")
    Base.metadata.drop_all(bind=engine)
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)

    print("Chargement des données de test...")
    seed_data.main()
    print("Base réinitialisée.")


if __name__ == "__main__":
    main()