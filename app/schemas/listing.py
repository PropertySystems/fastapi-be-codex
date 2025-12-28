import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PropertyType(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    LAND = "land"
    OFFICE = "office"


class ListingType(str, Enum):
    SALE = "sale"
    RENT = "rent"


class ListingBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    property_type: PropertyType
    listing_type: ListingType
    price: float = Field(..., ge=0)
    currency: str = Field(..., min_length=3, max_length=3)
    city: str = Field(..., max_length=100)
    area_sqm: int = Field(..., gt=0)
    rooms: int = Field(..., ge=0)


class ListingCreate(ListingBase):
    pass


class ListingRead(ListingBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
