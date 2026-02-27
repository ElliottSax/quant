"""Add hybrid model fields to users table.

Revision ID: 010
Revises: 009_add_prediction_models
Create Date: 2026-02-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010_add_hybrid_model_fields'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add hybrid model fields to users table."""
    # Add subscription-related fields
    op.add_column('users', sa.Column('ad_free', sa.Boolean(), nullable=False, server_default='false'))

    # Add referral tracking fields
    op.add_column('users', sa.Column('referral_code', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('referral_credit_balance', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('users', sa.Column('referred_by_user_id', sa.String(36), nullable=True))

    # Create indexes for faster lookups
    op.create_index(op.f('ix_users_referral_code'), 'users', ['referral_code'], unique=True)
    op.create_index(op.f('ix_users_referred_by'), 'users', ['referred_by_user_id'], unique=False)

    # Update subscription_tier constraint to include new tier names
    # Note: This drops the old constraint and creates a new one
    op.drop_constraint('valid_subscription_tier', 'users', type_='check')
    op.create_check_constraint(
        'valid_subscription_tier',
        'users',
        "subscription_tier IN ('free', 'starter', 'professional', 'enterprise')"
    )


def downgrade() -> None:
    """Revert hybrid model fields from users table."""
    # Drop indexes
    op.drop_index(op.f('ix_users_referral_code'), table_name='users')
    op.drop_index(op.f('ix_users_referred_by'), table_name='users')

    # Drop columns
    op.drop_column('users', 'referred_by_user_id')
    op.drop_column('users', 'referral_credit_balance')
    op.drop_column('users', 'referral_code')
    op.drop_column('users', 'ad_free')

    # Revert subscription_tier constraint to old tier names
    op.drop_constraint('valid_subscription_tier', 'users', type_='check')
    op.create_check_constraint(
        'valid_subscription_tier',
        'users',
        "subscription_tier IN ('free', 'premium', 'enterprise')"
    )
