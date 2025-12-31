from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import set_committed_value

from app.models.user import User, UserRole
from app.repositories.listing_repository import ListingRepository
from app.schemas.listing import ListingCreate, ListingImageRead, ListingRead
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
