from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.panne import GravitePanne, StatutPanne, TypePanne

class PanneCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    transformateur_id: int = Field(gt=0)
    type_panne: TypePanne
    gravite: GravitePanne
    description: str = Field(min_length=3, max_length=2000)

class PanneUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    statut: StatutPanne | None = None
    gravite: GravitePanne | None = None
    description: str | None = Field(default=None, min_length=3, max_length=2000)
    actions_correctives: str | None = Field(default=None, max_length=2000)

class PanneRead(BaseModel):
    id: int
    transformateur_id: int
    transformateur_reference: str
    transformateur_nom: str
    secteur: str
    type_panne: TypePanne
    gravite: GravitePanne
    description: str
    statut: StatutPanne
    active: bool
    signale_par: str
    date_signalement: datetime
    date_resolution: datetime | None
    actions_correctives: str | None
    resolu_par: str | None
    updated_at: datetime
