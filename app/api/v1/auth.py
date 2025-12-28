from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.user import Token, UserCreate, UserLogin, UserRead
from app.services.auth_service import AuthService, get_auth_service, require_roles
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_service() -> UserService:
    return UserService()


authenticated_roles = (UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.create_user(session, payload)


@router.post("/login", response_model=Token)
async def login(
    payload: UserLogin,
    session: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.login(session, payload)


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(require_roles(authenticated_roles))) -> UserRead:
    return UserRead.model_validate(current_user)
