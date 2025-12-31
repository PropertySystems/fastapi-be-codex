import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.user import UserRead, UserUpdate
from app.services.auth_service import require_roles
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service() -> UserService:
    return UserService()


admin_roles = (UserRole.ADMIN,)


@router.get("/", response_model=list[UserRead])
async def list_users(
    session: AsyncSession = Depends(get_session),
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_roles(admin_roles)),
) -> list[UserRead]:
    return await service.list_users(session)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_roles(admin_roles)),
) -> UserRead:
    return await service.get_user(session, user_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_roles(admin_roles)),
) -> UserRead:
    return await service.update_user(session, user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    service: UserService = Depends(get_user_service),
    _: User = Depends(require_roles(admin_roles)),
) -> None:
    await service.delete_user(session, user_id)
    return None
