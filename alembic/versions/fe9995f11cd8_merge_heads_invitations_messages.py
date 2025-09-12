"""Merge heads invitations+messages

Revision ID: fe9995f11cd8
Revises: fe_add_invitation_code, fe_add_messages_table
Create Date: 2025-09-12 16:47:31.645277

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe9995f11cd8'
down_revision = ('fe_add_invitation_code', 'fe_add_messages_table')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
