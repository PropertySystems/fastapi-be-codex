from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.listing import (
    ListingCreate,
    ListingImageRead,
    ListingListRead,
    ListingRead,
    ListingSortField,
    ListingUpdate,
    ListingType,
    PropertyType,
    SortOrder,
)
from app.services.auth_service import require_roles
from app.services.listing_service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


def get_listing_service() -> ListingService:
    return ListingService()


@router.get("", response_model=ListingListRead)
async def list_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: ListingSortField = Query(ListingSortField.CREATED_AT),
    sort_order: SortOrder = Query(SortOrder.DESC),
    property_type: PropertyType | None = Query(None),
    listing_type: ListingType | None = Query(None),
    city: str | None = Query(None, max_length=100),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    min_area: int | None = Query(None, ge=1),
    max_area: int | None = Query(None, ge=1),
    min_rooms: int | None = Query(None, ge=0),
    max_rooms: int | None = Query(None, ge=0),
    session: AsyncSession = Depends(get_session),
    service: ListingService = Depends(get_listing_service),
) -> ListingListRead:
    return await service.list_listings(
        session,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        property_type=property_type,
        listing_type=listing_type,
        city=city,
        min_price=min_price,
        max_price=max_price,
        min_area=min_area,
        max_area=max_area,
        min_rooms=min_rooms,
        max_rooms=max_rooms,
    )


@router.get("/me", response_model=ListingListRead)
async def list_my_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: ListingSortField = Query(ListingSortField.CREATED_AT),
    sort_order: SortOrder = Query(SortOrder.DESC),
    property_type: PropertyType | None = Query(None),
    listing_type: ListingType | None = Query(None),
    city: str | None = Query(None, max_length=100),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    min_area: int | None = Query(None, ge=1),
    max_area: int | None = Query(None, ge=1),
    min_rooms: int | None = Query(None, ge=0),
    max_rooms: int | None = Query(None, ge=0),
    session: AsyncSession = Depends(get_session),
    service: ListingService = Depends(get_listing_service),
    current_user: User = Depends(
        require_roles((UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN))
    ),
) -> ListingListRead:
    return await service.list_user_listings(
        session,
        user=current_user,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        property_type=property_type,
        listing_type=listing_type,
        city=city,
        min_price=min_price,
        max_price=max_price,
        min_area=min_area,
        max_area=max_area,
        min_rooms=min_rooms,
        max_rooms=max_rooms,
    )


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


@router.get("/{listing_id}", response_model=ListingRead)
async def get_listing(
    listing_id: UUID,
    session: AsyncSession = Depends(get_session),
    service: ListingService = Depends(get_listing_service),
) -> ListingRead:
    return await service.get_listing(session, listing_id)


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


@router.patch("/{listing_id}", response_model=ListingRead)
async def update_listing(
    listing_id: UUID,
    payload: ListingUpdate,
    session: AsyncSession = Depends(get_session),
    service: ListingService = Depends(get_listing_service),
    current_user: User = Depends(
        require_roles((UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN))
    ),
) -> ListingRead:
    return await service.update_listing(session, listing_id, payload, current_user)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: UUID,
    session: AsyncSession = Depends(get_session),
    service: ListingService = Depends(get_listing_service),
    current_user: User = Depends(
        require_roles((UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN))
    ),
) -> None:
    await service.delete_listing(session, listing_id, current_user)
