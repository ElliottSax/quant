"""initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""

    # Create politicians table
    op.create_table(
        'politicians',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('chamber', sa.String(length=10), nullable=False),
        sa.Column('party', sa.String(length=20), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('bioguide_id', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bioguide_id'),
        sa.CheckConstraint("chamber IN ('senate', 'house')", name='politicians_chamber_check')
    )

    # Create indexes on politicians
    op.create_index('ix_politicians_name', 'politicians', ['name'])
    op.create_index('ix_politicians_chamber', 'politicians', ['chamber'])
    op.create_index('ix_politicians_party', 'politicians', ['party'])

    # Create tickers table
    op.create_table(
        'tickers',
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('symbol')
    )

    # Create trades table
    # Note: For TimescaleDB hypertables, the partitioning column (transaction_date)
    # must be part of the primary key
    op.create_table(
        'trades',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('politician_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('transaction_type', sa.String(length=10), nullable=False),
        sa.Column('amount_min', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('amount_max', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('disclosure_date', sa.Date(), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id', 'transaction_date'),  # Composite key for TimescaleDB
        sa.ForeignKeyConstraint(['politician_id'], ['politicians.id'], ondelete='CASCADE'),
        sa.CheckConstraint("transaction_type IN ('buy', 'sell')", name='trades_transaction_type_check')
    )

    # Create indexes on trades
    op.create_index('ix_trades_politician_id', 'trades', ['politician_id'])
    op.create_index('ix_trades_ticker', 'trades', ['ticker'])
    op.create_index('ix_trades_transaction_date', 'trades', ['transaction_date'])

    # Convert trades table to TimescaleDB hypertable
    # This requires TimescaleDB extension to be enabled
    # NOTE: Commented out for testing environment - uncomment for production
    # op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
    # op.execute("SELECT create_hypertable('trades', 'transaction_date', if_not_exists => TRUE);")


def downgrade() -> None:
    """Drop all tables."""
    # Drop trades table (hypertable)
    op.drop_index('ix_trades_transaction_date', table_name='trades')
    op.drop_index('ix_trades_ticker', table_name='trades')
    op.drop_index('ix_trades_politician_id', table_name='trades')
    op.drop_table('trades')

    # Drop tickers table
    op.drop_table('tickers')

    # Drop politicians table
    op.drop_index('ix_politicians_party', table_name='politicians')
    op.drop_index('ix_politicians_chamber', table_name='politicians')
    op.drop_index('ix_politicians_name', table_name='politicians')
    op.drop_table('politicians')
