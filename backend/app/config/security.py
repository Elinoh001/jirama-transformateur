from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.config.settings import settings

# bcrypt ne prend en compte que les 72 premiers octets du mot de passe.
_BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    """Retourne le hash bcrypt du mot de passe (jamais le mot de passe en clair)."""
    secret = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(secret, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Compare un mot de passe en clair avec son hash."""
    try:
        secret = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
        return bcrypt.checkpw(secret, hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int, role: str) -> str:
    """Crée un JWT signé contenant l'id utilisateur (sub), son rôle et la date d'expiration."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Décode et valide un JWT. Retourne None si le token est invalide ou expiré."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        return None