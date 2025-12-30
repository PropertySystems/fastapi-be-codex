from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "202409010000"
down_revision = "202407170002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "listing_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["listing_id"], ["listings.id"], name="fk_listing_images_listing_id", ondelete="CASCADE"
        ),
    )


def downgrade() -> None:
    op.drop_table("listing_images")
