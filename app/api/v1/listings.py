from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.listing import ListingCreate, ListingRead
from app.services.auth_service import require_roles
from app.services.listing_service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


def get_listing_service() -> ListingService:
    return ListingService()


@router.post("", response_model=ListingRead, status_code=status.HTTP_201_CREATED)
async def create_listing(
    payload: ListingCreate,
    session: AsyncSession = Depends(get_session),
    service: ListingService = Depends(get_listing_service),
    _current_user: User = Depends(
        require_roles((UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN))
    ),
) -> ListingRead:
    return await service.create_listing(session, payload)
