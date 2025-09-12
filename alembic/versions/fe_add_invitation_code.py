"""
add code field to invitations

Revision ID: fe_add_invitation_code
Revises: e460490c0896
Create Date: 2025-09-11 15:30:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe_add_invitation_code'
down_revision = 'a94d7c678de4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('invitations', sa.Column('code', sa.String(length=64), nullable=True))
    op.create_index('ix_invitations_code', 'invitations', ['code'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_invitations_code', table_name='invitations')
    op.drop_column('invitations', 'code')


