"""Add API keys and mobile devices tables

Revision ID: add_api_keys_devices
Revises:
Create Date: 2026-02-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_api_keys_devices'
down_revision = 'add_analytics_20260203'
branch_labels = None
depends_on = None


def upgrade():
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('key_id', sa.String(16), nullable=False),
        sa.Column('key_hash', sa.String(64), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('permissions', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_requests', sa.String(), nullable=False, server_default='0'),
        sa.Column('key_metadata', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for api_keys
    op.create_index('ix_api_keys_user_id', 'api_keys', ['user_id'])
    op.create_index('ix_api_keys_key_id', 'api_keys', ['key_id'], unique=True)
    op.create_index('ix_api_keys_key_hash', 'api_keys', ['key_hash'], unique=True)

    # Create mobile_devices table
    op.create_table(
        'mobile_devices',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('device_token', sa.String(500), nullable=False),
        sa.Column('device_type', sa.String(20), nullable=False),
        sa.Column('app_version', sa.String(50), nullable=False),
        sa.Column('device_model', sa.String(100), nullable=True),
        sa.Column('os_version', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('device_metadata', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for mobile_devices
    op.create_index('ix_mobile_devices_user_id', 'mobile_devices', ['user_id'])
    op.create_index('ix_mobile_devices_device_token', 'mobile_devices', ['device_token'], unique=True)
    op.create_index('idx_device_user_type', 'mobile_devices', ['user_id', 'device_type'])


def downgrade():
    # Drop mobile_devices table
    op.drop_index('idx_device_user_type', 'mobile_devices')
    op.drop_index('ix_mobile_devices_device_token', 'mobile_devices')
    op.drop_index('ix_mobile_devices_user_id', 'mobile_devices')
    op.drop_table('mobile_devices')

    # Drop api_keys table
    op.drop_index('ix_api_keys_key_hash', 'api_keys')
    op.drop_index('ix_api_keys_key_id', 'api_keys')
    op.drop_index('ix_api_keys_user_id', 'api_keys')
    op.drop_table('api_keys')
