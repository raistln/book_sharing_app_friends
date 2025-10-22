"""Add notifications table

Revision ID: add_notifications_001
Revises: zz_update_books_fields
Create Date: 2025-10-22 11:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_notifications_001'
down_revision = 'zz_update_books_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.Enum(
            'LOAN_REQUEST', 'LOAN_APPROVED', 'LOAN_REJECTED', 'LOAN_RETURNED',
            'DUE_DATE_REMINDER', 'OVERDUE', 'NEW_MESSAGE', 'GROUP_INVITATION', 'GROUP_JOINED',
            name='notificationtype'
        ), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='notificationpriority'), nullable=False, server_default='medium'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('read_at', sa.DateTime(), nullable=True),
    )
    
    # Create indexes for better performance
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])
    op.create_index('ix_notifications_type', 'notifications', ['type'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_notifications_type', table_name='notifications')
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    
    # Drop table
    op.drop_table('notifications')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS notificationtype')
    op.execute('DROP TYPE IF EXISTS notificationpriority')
