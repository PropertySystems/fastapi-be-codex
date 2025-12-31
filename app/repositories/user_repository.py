import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserCreate


class UserRepository:
    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, session: AsyncSession, user_id: uuid.UUID) -> User | None:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, user_data: UserCreate, hashed_password: str) -> User:
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            hashed_password=hashed_password,
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    async def list_all(self, session: AsyncSession) -> list[User]:
        result = await session.execute(select(User))
        return list(result.scalars().all())

    async def update(
        self,
        session: AsyncSession,
        user: User,
        *,
        email: str | None = None,
        full_name: str | None = None,
        role: UserRole | None = None,
        hashed_password: str | None = None,
    ) -> User:
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        if role is not None:
            user.role = role
        if hashed_password is not None:
            user.hashed_password = hashed_password
        await session.flush()
        await session.refresh(user)
        return user

    async def delete(self, session: AsyncSession, user: User) -> None:
        await session.delete(user)
