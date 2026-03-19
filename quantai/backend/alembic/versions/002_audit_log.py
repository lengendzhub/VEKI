# backend/alembic/versions/002_audit_log.py
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "002_audit_log"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_audit_actor_ts", "audit_logs", ["actor", "timestamp"])
    op.create_index("ix_audit_entity", "audit_logs", ["entity_type", "entity_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_actor_ts", table_name="audit_logs")
    op.drop_index("ix_audit_entity", table_name="audit_logs")
    op.drop_table("audit_logs")
