from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "202407170000"
down_revision = None
branch_labels = None
depends_on = None

property_type_enum = postgresql.ENUM(
    "apartment", "house", "land", "office", name="property_type_enum"
)
listing_type_enum = postgresql.ENUM("sale", "rent", name="listing_type_enum")


def upgrade() -> None:
    bind = op.get_bind()
    property_type_enum.create(bind, checkfirst=True)
    listing_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("property_type", property_type_enum, nullable=False),
        sa.Column("listing_type", listing_type_enum, nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("area_sqm", sa.Integer(), nullable=False),
        sa.Column("rooms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_listings_price_non_negative"),
        sa.CheckConstraint("area_sqm > 0", name="ck_listings_area_positive"),
        sa.CheckConstraint("rooms >= 0", name="ck_listings_rooms_non_negative"),
    )


def downgrade() -> None:
    op.drop_table("listings")
    bind = op.get_bind()
    listing_type_enum.drop(bind, checkfirst=True)
    property_type_enum.drop(bind, checkfirst=True)
