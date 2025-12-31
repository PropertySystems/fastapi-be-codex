from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import set_committed_value

from app.models.user import User, UserRole
from app.repositories.listing_repository import ListingRepository
from app.schemas.listing import (
    ListingCreate,
    ListingImageRead,
    ListingListRead,
    ListingRead,
    ListingSortField,
    ListingUpdate,
    SortOrder,
)
from app.services.storage_service import GCSStorageService, StorageService


class ListingService:
    def __init__(
        self,
        repository: ListingRepository | None = None,
        storage_service: StorageService | None = None,
    ) -> None:
        self.repository = repository or ListingRepository()
        self.storage_service = storage_service

    async def create_listing(
        self, session: AsyncSession, listing: ListingCreate, user: User
    ) -> ListingRead:
        created = await self.repository.create(session, listing, user.id)
        # Avoid lazy-loading images during response serialization.
        set_committed_value(created, "images", [])
        return ListingRead.model_validate(created)

    async def upload_listing_image(
        self, session: AsyncSession, listing_id: UUID, file: UploadFile, user: User
    ) -> ListingImageRead:
        listing = await self.repository.get_by_id(session, listing_id)
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
            )

        if user.role == UserRole.USER and listing.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to modify this listing",
            )

        storage = self.storage_service or GCSStorageService()
        self.storage_service = storage

        image_url = await storage.upload_listing_image(file, listing_id)
        image = await self.repository.add_image(session, listing_id, image_url)
        return ListingImageRead.model_validate(image)

    async def update_listing(
        self, session: AsyncSession, listing_id: UUID, listing: ListingUpdate, user: User
    ) -> ListingRead:
        existing_listing = await self.repository.get_by_id(session, listing_id)

        if not existing_listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
            )

        if user.role == UserRole.USER and existing_listing.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to modify this listing",
            )

        updated_listing = await self.repository.update(session, existing_listing, listing)
        return ListingRead.model_validate(updated_listing)

    async def list_listings(
        self,
        session: AsyncSession,
        *,
        page: int,
        page_size: int,
        sort_by: ListingSortField,
        sort_order: SortOrder,
        property_type: str | None = None,
        listing_type: str | None = None,
        city: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_area: int | None = None,
        max_area: int | None = None,
        min_rooms: int | None = None,
        max_rooms: int | None = None,
    ) -> ListingListRead:
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum price cannot exceed maximum price",
            )

        if min_area is not None and max_area is not None and min_area > max_area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum area cannot exceed maximum area",
            )

        if min_rooms is not None and max_rooms is not None and min_rooms > max_rooms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum rooms cannot exceed maximum rooms",
            )

        listings, total = await self.repository.list(
            session,
            page=page,
            page_size=page_size,
            sort_field=sort_by.value,
            sort_descending=sort_order == SortOrder.DESC,
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

        return ListingListRead(
            items=[ListingRead.model_validate(listing) for listing in listings],
            total=total,
            page=page,
            page_size=page_size,
        )
