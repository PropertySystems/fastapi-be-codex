from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead


class UserService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    async def create_user(self, session: AsyncSession, payload: UserCreate) -> UserRead:
        existing = await self.repository.get_by_email(session, payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        hashed_password = get_password_hash(payload.password)
        user = await self.repository.create(session, payload, hashed_password)
        return UserRead.model_validate(user)
