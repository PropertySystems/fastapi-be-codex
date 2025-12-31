import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate


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

    async def list_users(self, session: AsyncSession) -> list[UserRead]:
        users = await self.repository.list_all(session)
        return [UserRead.model_validate(user) for user in users]

    async def get_user(self, session: AsyncSession, user_id: uuid.UUID) -> UserRead:
        user = await self.repository.get_by_id(session, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return UserRead.model_validate(user)

    async def update_user(
        self, session: AsyncSession, user_id: uuid.UUID, payload: UserUpdate
    ) -> UserRead:
        user = await self.repository.get_by_id(session, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        if payload.email and payload.email != user.email:
            existing = await self.repository.get_by_email(session, payload.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email already exists.",
                )

        hashed_password = (
            get_password_hash(payload.password) if payload.password is not None else None
        )

        updated_user = await self.repository.update(
            session,
            user,
            email=payload.email,
            full_name=payload.full_name,
            role=payload.role,
            hashed_password=hashed_password,
        )
        return UserRead.model_validate(updated_user)

    async def delete_user(self, session: AsyncSession, user_id: uuid.UUID) -> None:
        user = await self.repository.get_by_id(session, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        await self.repository.delete(session, user)
