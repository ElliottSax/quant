"""add performance indexes for common query patterns

Revision ID: 004
Revises: 003
Create Date: 2025-12-05

This migration adds database indexes to optimize common query patterns:
- Transaction date queries (sorting by date)
- Politician + date queries (per-politician trade history)
- Ticker + date queries (stock-specific trade tracking)
- Disclosure date queries (compliance monitoring)

Expected Performance Improvement:
- 50-70% faster trade list queries
- 60-80% faster politician trade history queries
- 70-90% faster ticker-specific queries

Index Sizing Estimates (for 100k trades):
- idx_trades_transaction_date: ~2-3 MB
- idx_trades_disclosure_date: ~2-3 MB
- idx_trades_politician_date: ~4-5 MB (composite)
- idx_trades_ticker_date: ~4-5 MB (composite)
- idx_trades_ticker: ~2-3 MB
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes to trades table."""

    # Index for transaction date queries (most common sorting)
    # Used in: GET /trades?skip=0&limit=100 (default sort)
    op.create_index(
        'idx_trades_transaction_date',
        'trades',
        ['transaction_date'],
        postgresql_using='btree',
        postgresql_ops={'transaction_date': 'DESC'}
    )

    # Index for disclosure date queries
    # Used in: Compliance monitoring, recent disclosure queries
    op.create_index(
        'idx_trades_disclosure_date',
        'trades',
        ['disclosure_date'],
        postgresql_using='btree',
        postgresql_ops={'disclosure_date': 'DESC'}
    )

    # Composite index for politician + date queries (common pattern)
    # Used in: GET /politicians/{id}/trades, politician trade history
    op.create_index(
        'idx_trades_politician_date',
        'trades',
        ['politician_id', 'transaction_date'],
        postgresql_using='btree',
        postgresql_ops={'transaction_date': 'DESC'}
    )

    # Composite index for ticker + date (stock-specific queries)
    # Used in: GET /trades?ticker=AAPL, stock price correlation
    op.create_index(
        'idx_trades_ticker_date',
        'trades',
        ['ticker', 'transaction_date'],
        postgresql_using='btree',
        postgresql_ops={'transaction_date': 'DESC'}
    )

    # Simple ticker index for ticker-only filters
    # Used in: Ticker autocomplete, ticker existence checks
    op.create_index(
        'idx_trades_ticker',
        'trades',
        ['ticker'],
        postgresql_using='btree'
    )

    # Transaction type index for buy/sell filtering
    # Used in: GET /trades?transaction_type=buy
    # Note: Low cardinality (only 2 values), but useful for combined filters
    op.create_index(
        'idx_trades_transaction_type',
        'trades',
        ['transaction_type'],
        postgresql_using='btree'
    )


def downgrade():
    """Remove performance indexes from trades table."""
    op.drop_index('idx_trades_transaction_type', table_name='trades')
    op.drop_index('idx_trades_ticker', table_name='trades')
    op.drop_index('idx_trades_ticker_date', table_name='trades')
    op.drop_index('idx_trades_politician_date', table_name='trades')
    op.drop_index('idx_trades_disclosure_date', table_name='trades')
    op.drop_index('idx_trades_transaction_date', table_name='trades')
