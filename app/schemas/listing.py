import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PropertyType(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    LAND = "land"
    OFFICE = "office"


class ListingType(str, Enum):
    SALE = "sale"
    RENT = "rent"


class ListingSortField(str, Enum):
    CREATED_AT = "created_at"
    PRICE = "price"
    AREA_SQM = "area_sqm"
    ROOMS = "rooms"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


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

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("property_type", "listing_type", mode="before")
    @classmethod
    def normalize_enum_values(cls, value: str | Enum) -> str | Enum:
        if isinstance(value, str):
            return value.lower()
        return value


class ListingCreate(ListingBase):
    pass


class ListingUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    property_type: PropertyType | None = None
    listing_type: ListingType | None = None
    price: float | None = Field(None, ge=0)
    currency: str | None = Field(None, min_length=3, max_length=3)
    city: str | None = Field(None, max_length=100)
    area_sqm: int | None = Field(None, gt=0)
    rooms: int | None = Field(None, ge=0)

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("property_type", "listing_type", mode="before")
    @classmethod
    def normalize_enum_values(cls, value: str | Enum | None) -> str | Enum | None:
        if isinstance(value, str):
            return value.lower()
        return value


class ListingImageRead(BaseModel):
    id: uuid.UUID
    url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ListingRead(ListingBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    images: list[ListingImageRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ListingListRead(BaseModel):
    items: list[ListingRead]
    total: int
    page: int
    page_size: int
