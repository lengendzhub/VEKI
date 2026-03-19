# backend/alembic/versions/001_initial.py
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("username", sa.String(length=64), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False, server_default="user"),
        sa.Column("telegram_chat_id", sa.String(length=64), nullable=True),
        sa.Column("device_token", sa.String(length=512), nullable=True),
        sa.Column("device_platform", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("users")
