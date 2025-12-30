from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.listing import ListingCreate, ListingImageRead, ListingRead
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
    current_user: User = Depends(
        require_roles((UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN))
    ),
) -> ListingRead:
    return await service.create_listing(session, payload, current_user)


@router.post(
    "/{listing_id}/images",
    response_model=ListingImageRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_listing_image(
    listing_id: UUID,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    service: ListingService = Depends(get_listing_service),
    current_user: User = Depends(
        require_roles((UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN))
    ),
) -> ListingImageRead:
    return await service.upload_listing_image(session, listing_id, file, current_user)
