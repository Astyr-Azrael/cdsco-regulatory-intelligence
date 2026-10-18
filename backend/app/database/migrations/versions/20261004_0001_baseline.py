"""Baseline provenance, canonical entity and usage schema."""

from alembic import op

from backend.app.database.models import Base

revision = "20261004_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The baseline creates the exact SQLAlchemy schema on a new database.
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
