from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings
from app.models.user import UserRole

# bcrypt_sha256 avoids bcrypt's 72-byte input limit while remaining compatible with bcrypt hashes.
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    exp: datetime


def create_access_token(subject: str, role: UserRole, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode = {"sub": subject, "role": role.value, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.token_algorithm)


def decode_access_token(token: str) -> TokenPayload:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.token_algorithm])
        token_data = TokenPayload.model_validate(payload)
    except JWTError as exc:  # pragma: no cover - library errors mapped to HTTP
        raise credentials_exception from exc
    except ValueError as exc:  # pragma: no cover - validation errors mapped to HTTP
        raise credentials_exception from exc
    return token_data
