from datetime import timedelta
from typing import Iterable
import uuid
import uuid
from datetime import timedelta
from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token, verify_password
from app.db.session import get_session
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import Token, UserLogin

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_auth_service() -> "AuthService":
    return AuthService()


class AuthService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    async def login(self, session: AsyncSession, payload: UserLogin) -> Token:
        user = await self.repository.get_by_email(session, payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            subject=str(user.id),
            role=user.role,
            expires_delta=expires,
        )
        return Token(access_token=access_token)

    async def resolve_current_user(
        self,
        session: AsyncSession,
        credentials: HTTPAuthorizationCredentials,
    ) -> User:
        token_data = decode_access_token(credentials.credentials)
        try:
            user_id = uuid.UUID(token_data.sub)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        user = await self.repository.get_by_id(session, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
    repository: UserRepository = Depends(get_user_repository),
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = decode_access_token(credentials.credentials)
    try:
        user_id = uuid.UUID(token_data.sub)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    user = await repository.get_by_id(session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(allowed_roles: Iterable[UserRole]):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this resource.",
            )
        return user

    return dependency
