from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.listing_repository import ListingRepository
from app.schemas.listing import ListingCreate, ListingRead


class ListingService:
    def __init__(self, repository: ListingRepository | None = None) -> None:
        self.repository = repository or ListingRepository()

    async def create_listing(
        self, session: AsyncSession, listing: ListingCreate, user: User
    ) -> ListingRead:
        created = await self.repository.create(session, listing, user.id)
        return ListingRead.model_validate(created)
