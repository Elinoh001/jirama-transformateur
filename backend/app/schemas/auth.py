from pydantic import BaseModel, Field, field_validator

from app.schemas.utilisateur import EmailLocal, UtilisateurRead, valider_force_mot_de_passe


class LoginRequest(BaseModel):
    email: EmailLocal
    password: str = Field(min_length=1, max_length=200)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UtilisateurRead


class ChangePasswordRequest(BaseModel):
    ancien_mot_de_passe: str = Field(min_length=1, max_length=200)
    nouveau_mot_de_passe: str = Field(max_length=200)

    @field_validator("nouveau_mot_de_passe")
    @classmethod
    def verifier_nouveau(cls, v: str) -> str:
        return valider_force_mot_de_passe(v)


class MessageResponse(BaseModel):
    message: str
