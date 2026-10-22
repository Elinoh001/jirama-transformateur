"""
Initialise la base de données :
  1. teste la connexion PostgreSQL
  2. active l'extension PostGIS si nécessaire
  3. crée toutes les tables

Usage (depuis le dossier backend) :
    python -m scripts.init_db
"""
from sqlalchemy import inspect, text

from app.database.base import Base
from app.database.connection import engine

# Importer les modèles est indispensable pour que Base.metadata les connaisse.
import app.models  # noqa: F401


def main() -> None:
    print("1) Connexion à PostgreSQL...")
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version()")).scalar()
        print(f"   OK : {version}")

    print("2) Activation de PostGIS...")
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        postgis = conn.execute(text("SELECT PostGIS_Lib_Version()")).scalar()
        print(f"   OK : PostGIS {postgis}")

    print("3) Création des tables...")
    Base.metadata.create_all(bind=engine)

    tables = sorted(inspect(engine).get_table_names())
    print("   Tables présentes :")
    for name in tables:
        print(f"   - {name}")

    print("\nInitialisation terminée avec succès.")


if __name__ == "__main__":
    main()