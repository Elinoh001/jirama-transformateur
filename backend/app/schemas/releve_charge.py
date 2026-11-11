from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReleveChargeCreate(BaseModel):
    """
    Saisie d'un relevé de charge. Il faut fournir AU MOINS une des deux mesures :
      - puissance_mesuree : puissance apparente en kVA ;
      - courant_mesure    : courant de ligne en A (triphasé). La puissance est alors estimée :
                            S (kVA) = racine(3) x U_BT (V) x I (A) / 1000.
    Les valeurs négatives, infinies ou non numériques sont refusées.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    transformateur_id: int = Field(gt=0)
    date_releve: date
    puissance_mesuree: float | None = Field(default=None, ge=0, allow_inf_nan=False, description="kVA")
    courant_mesure: float | None = Field(default=None, ge=0, allow_inf_nan=False, description="A")
    # Si absent, le backend utilise le nom de l'utilisateur connecté.
    releve_par: str | None = Field(default=None, min_length=1, max_length=150)

    @model_validator(mode="after")
    def valider_coherence(self) -> "ReleveChargeCreate":
        if self.puissance_mesuree is None and self.courant_mesure is None:
            raise ValueError("Saisir la puissance mesurée (kVA) ou le courant mesuré (A)")
        if self.date_releve > date.today():
            raise ValueError("La date d'un relevé ne peut pas être dans le futur")
        return self


class ReleveChargeRead(BaseModel):
    id: int
    transformateur_id: int
    transformateur_reference: str
    transformateur_nom: str
    date_releve: date
    puissance_mesuree: float  # kVA
    courant_mesure: float | None  # A
    puissance_nominale: float  # kVA
    taux_charge: float  # % = puissance mesurée / puissance nominale x 100
    surcharge: bool  # True si taux_charge > 100 %
    alerte: str | None  # message d'alerte de surcharge, sinon None
    releve_par: str
    created_at: datetime
