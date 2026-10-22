from pydantic import BaseModel, Field

from app.schemas.utilisateur import EmailLocal, UtilisateurRead


class LoginRequest(BaseModel):
    email: EmailLocal
    password: str = Field(min_length=1, max_length=200)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UtilisateurRead