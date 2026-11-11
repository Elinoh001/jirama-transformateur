"""
Recalcule la prochaine inspection prévue de TOUS les transformateurs.

À lancer une fois après la mise à jour de la gestion des échéances, pour que les données déjà
présentes en base (inspections planifiées, périodicités) soient prises en compte.
Le script est rejouable sans danger.

Usage (depuis le dossier backend) :
    python -m scripts.recalculer_echeances
"""
from sqlalchemy import select

from app.database.connection import SessionLocal
from app.models.transformateur import Transformateur
from app.services.echeance_inspection import synchroniser_prochaine_inspection


def main() -> None:
    with SessionLocal() as db:
        transformateurs = db.scalars(select(Transformateur).order_by(Transformateur.reference)).all()
        for t in transformateurs:
            avant = t.prochaine_inspection
            situation = synchroniser_prochaine_inspection(db, t)
            marque = "" if avant == situation.prochaine_prevue else "  <- mis à jour"
            retard = f"  RETARD {situation.jours_retard} j" if situation.en_retard else ""
            print(
                f"{t.reference}: prévue {situation.prochaine_prevue} ({situation.source}), "
                f"théorique {situation.echeance_theorique}{retard}{marque}"
            )
        db.commit()
        print(f"{len(transformateurs)} transformateur(s) recalculé(s).")


if __name__ == "__main__":
    main()
