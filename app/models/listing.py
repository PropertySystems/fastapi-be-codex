import enum
import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, Enum, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class PropertyType(str, enum.Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    LAND = "land"
    OFFICE = "office"


class ListingType(str, enum.Enum):
    SALE = "sale"
    RENT = "rent"


class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    property_type = Column(Enum(PropertyType, name="property_type_enum"), nullable=False)
    listing_type = Column(Enum(ListingType, name="listing_type_enum"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    city = Column(String(100), nullable=False)
    area_sqm = Column(Integer, nullable=False)
    rooms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_listings_price_non_negative"),
        CheckConstraint("area_sqm > 0", name="ck_listings_area_positive"),
        CheckConstraint("rooms >= 0", name="ck_listings_rooms_non_negative"),
    )
