from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing
from app.schemas.listing import ListingCreate


class ListingRepository:
    async def create(self, session: AsyncSession, listing_data: ListingCreate) -> Listing:
        listing = Listing(**listing_data.model_dump())
        session.add(listing)
        await session.flush()
        await session.refresh(listing)
        return listing
