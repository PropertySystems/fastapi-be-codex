from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing
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
