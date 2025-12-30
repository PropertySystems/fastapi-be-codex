from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "202407170002"
down_revision = "202407170001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "listings",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_foreign_key(
        "fk_listings_user_id_users",
        "listings",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_listings_user_id_users", "listings", type_="foreignkey")
    op.drop_column("listings", "user_id")
