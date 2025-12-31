from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.listing import Listing
from app.models.listing_image import ListingImage
from app.schemas.listing import ListingCreate, ListingUpdate


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

    async def update(
        self, session: AsyncSession, listing: Listing, listing_data: ListingUpdate
    ) -> Listing:
        data = listing_data.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(listing, field, value)

        await session.flush()
        await session.refresh(listing)
        return listing

    async def add_image(
        self, session: AsyncSession, listing_id: UUID, url: str
    ) -> ListingImage:
        image = ListingImage(listing_id=listing_id, url=url)
        session.add(image)
        await session.flush()
        await session.refresh(image)
        return image

    async def delete(self, session: AsyncSession, listing: Listing) -> None:
        await session.delete(listing)
        await session.flush()

    async def list(
        self,
        session: AsyncSession,
        *,
        page: int,
        page_size: int,
        sort_field: str,
        sort_descending: bool,
        user_id: UUID | None = None,
        property_type: str | None = None,
        listing_type: str | None = None,
        city: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        min_area: int | None = None,
        max_area: int | None = None,
        min_rooms: int | None = None,
        max_rooms: int | None = None,
    ) -> tuple[list[Listing], int]:
        conditions = []
        if user_id:
            conditions.append(Listing.user_id == user_id)
        if property_type:
            conditions.append(Listing.property_type == property_type)
        if listing_type:
            conditions.append(Listing.listing_type == listing_type)
        if city:
            conditions.append(Listing.city.ilike(f"%{city}%"))
        if min_price is not None:
            conditions.append(Listing.price >= min_price)
        if max_price is not None:
            conditions.append(Listing.price <= max_price)
        if min_area is not None:
            conditions.append(Listing.area_sqm >= min_area)
        if max_area is not None:
            conditions.append(Listing.area_sqm <= max_area)
        if min_rooms is not None:
            conditions.append(Listing.rooms >= min_rooms)
        if max_rooms is not None:
            conditions.append(Listing.rooms <= max_rooms)

        sort_column = {
            "created_at": Listing.created_at,
            "price": Listing.price,
            "area_sqm": Listing.area_sqm,
            "rooms": Listing.rooms,
        }.get(sort_field, Listing.created_at)
        order_by_clause = (
            sort_column.desc() if sort_descending else sort_column.asc()
        )

        query = (
            select(Listing)
            .options(selectinload(Listing.images))
            .where(*conditions)
            .order_by(order_by_clause)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        listings_result = await session.execute(query)
        listings = listings_result.scalars().all()

        count_query = select(func.count()).select_from(Listing).where(*conditions)
        total = await session.scalar(count_query)

        return listings, int(total or 0)
