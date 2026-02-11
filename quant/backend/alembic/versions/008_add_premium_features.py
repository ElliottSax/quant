"""Add premium features: alerts, portfolios, subscriptions

Revision ID: 007_add_premium_features
Revises: 006_add_performance_indexes
Create Date: 2026-02-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_add_premium_features'
down_revision = '007_add_data_source_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""

    # Create enums
    alert_type_enum = postgresql.ENUM('trade', 'price', 'politician_activity', 'pattern', name='alert_type_enum', create_type=False)
    alert_type_enum.create(op.get_bind(), checkfirst=True)

    alert_status_enum = postgresql.ENUM('active', 'paused', 'triggered', 'expired', name='alert_status_enum', create_type=False)
    alert_status_enum.create(op.get_bind(), checkfirst=True)

    subscription_tier_enum = postgresql.ENUM('free', 'basic', 'premium', 'enterprise', name='subscription_tier_enum', create_type=False)
    subscription_tier_enum.create(op.get_bind(), checkfirst=True)

    subscription_status_enum = postgresql.ENUM('active', 'cancelled', 'past_due', 'trialing', 'paused', name='subscription_status_enum', create_type=False)
    subscription_status_enum.create(op.get_bind(), checkfirst=True)

    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('alert_type', alert_type_enum, nullable=False, index=True),
        sa.Column('conditions', postgresql.JSONB, nullable=False),
        sa.Column('notification_channels', postgresql.JSONB, nullable=False),
        sa.Column('webhook_url', sa.Text, nullable=True),
        sa.Column('notification_email', sa.String(255), nullable=True),
        sa.Column('status', alert_status_enum, nullable=False, server_default='active', index=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_triggered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trigger_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('alert_metadata', postgresql.JSONB, nullable=True),
    )

    # Create portfolios table
    op.create_table(
        'portfolios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('politician_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('politicians.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('snapshot_date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('holdings', postgresql.JSONB, nullable=False),
        sa.Column('total_value', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_cost_basis', sa.Numeric(15, 2), nullable=True),
        sa.Column('unrealized_gain_loss', sa.Numeric(15, 2), nullable=True),
        sa.Column('return_pct', sa.Numeric(10, 4), nullable=True),
        sa.Column('sector_allocation', postgresql.JSONB, nullable=True),
        sa.Column('concentration_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('diversification_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('portfolio_metadata', postgresql.JSONB, nullable=True),
    )

    # Create unique index for portfolio snapshots
    op.create_index(
        'idx_unique_portfolio_snapshot',
        'portfolios',
        ['politician_id', 'snapshot_date'],
        unique=True
    )

    # Create watchlists table
    op.create_table(
        'watchlists',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('politician_ids', postgresql.JSONB, nullable=False),
        sa.Column('is_public', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('sort_order', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('watchlist_metadata', postgresql.JSONB, nullable=True),
    )

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True, unique=True),
        sa.Column('tier', subscription_tier_enum, nullable=False, server_default='free', index=True),
        sa.Column('status', subscription_status_enum, nullable=False, server_default='active', index=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True, unique=True, index=True),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True, unique=True, index=True),
        sa.Column('stripe_price_id', sa.String(255), nullable=True),
        sa.Column('billing_cycle', sa.String(20), nullable=False, server_default='monthly'),
        sa.Column('price_per_period', sa.Numeric(10, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancel_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('api_rate_limit', sa.Integer, nullable=False, server_default='100'),
        sa.Column('features', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('subscription_metadata', postgresql.JSONB, nullable=True),
    )

    # Create usage_records table
    op.create_table(
        'usage_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('api_key_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('api_keys.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('resource_type', sa.String(50), nullable=False, index=True),
        sa.Column('endpoint', sa.String(255), nullable=True),
        sa.Column('request_count', sa.Integer, nullable=False, server_default='1'),
        sa.Column('usage_date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('usage_metadata', postgresql.JSONB, nullable=True),
    )

    # Create index for usage aggregation
    op.create_index(
        'idx_usage_aggregation',
        'usage_records',
        ['user_id', 'usage_date', 'resource_type']
    )


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop tables
    op.drop_table('usage_records')
    op.drop_table('subscriptions')
    op.drop_table('watchlists')
    op.drop_index('idx_unique_portfolio_snapshot', 'portfolios')
    op.drop_table('portfolios')
    op.drop_table('alerts')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS alert_type_enum')
    op.execute('DROP TYPE IF EXISTS alert_status_enum')
    op.execute('DROP TYPE IF EXISTS subscription_tier_enum')
    op.execute('DROP TYPE IF EXISTS subscription_status_enum')
