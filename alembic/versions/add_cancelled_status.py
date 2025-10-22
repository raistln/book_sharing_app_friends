"""Add cancelled status to loan_status enum

Revision ID: add_cancelled_status
Revises: add_notifications_001
Create Date: 2025-10-22 11:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_cancelled_status'
down_revision = 'add_notifications_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'cancelled' value to loan_status enum
    op.execute("ALTER TYPE loan_status ADD VALUE IF NOT EXISTS 'cancelled'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values directly
    # You would need to recreate the enum type without 'cancelled'
    # This is a simplified downgrade that doesn't actually remove the value
    pass
