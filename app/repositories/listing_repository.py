from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.listing import Listing
from app.models.listing_image import ListingImage
from app.schemas.listing import ListingCreate


class ListingRepository:
    async def create(
        self, session: AsyncSession, listing_data: ListingCreate, user_id: UUID
    ) -> Listing:
        listing = Listing(**listing_data.model_dump(), user_id=user_id)
        session.add(listing)
        await session.flush()
        await session.refresh(listing)
        return listing

    async def get_by_id(self, session: AsyncSession, listing_id: UUID) -> Listing | None:
        result = await session.execute(
            select(Listing)
                .options(selectinload(Listing.images))
                .where(Listing.id == listing_id)
        )
        return result.scalar_one_or_none()

    async def add_image(
        self, session: AsyncSession, listing_id: UUID, url: str
    ) -> ListingImage:
        image = ListingImage(listing_id=listing_id, url=url)
        session.add(image)
        await session.flush()
        await session.refresh(image)
        return image
