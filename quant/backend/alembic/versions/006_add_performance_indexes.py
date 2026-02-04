"""Add performance indexes

Revision ID: 006
Revises: 005
Create Date: 2026-01-28 12:00:00.000000

Adds additional indexes for query performance optimization:
- Composite indexes for common query patterns
- Covering indexes for frequently accessed columns
- Partial indexes for filtered queries
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes"""

    # Trades table - composite index for politician + date queries
    op.create_index(
        'idx_trades_politician_date',
        'trades',
        ['politician_id', 'transaction_date'],
        postgresql_using='btree'
    )

    # Trades table - composite index for symbol + date (market analysis)
    op.create_index(
        'idx_trades_ticker_date',
        'trades',
        ['ticker', 'transaction_date'],
        postgresql_using='btree'
    )

    # Trades table - composite index for transaction type + date (buy/sell analysis)
    op.create_index(
        'idx_trades_type_date',
        'trades',
        ['transaction_type', 'transaction_date'],
        postgresql_using='btree'
    )

    # Trades table - partial index for recent trades (last 90 days)
    op.execute("""
        CREATE INDEX idx_trades_recent
        ON trades (transaction_date DESC, disclosure_date DESC)
        WHERE transaction_date >= CURRENT_DATE - INTERVAL '90 days'
    """)

    # Trades table - partial index for large trades (>$1M)
    op.execute("""
        CREATE INDEX idx_trades_large
        ON trades (politician_id, ticker, transaction_date)
        WHERE amount_min >= 1000000 OR amount_max >= 1000000
    """)

    # Politicians table - composite index for chamber + party (filtering)
    op.create_index(
        'idx_politicians_chamber_party',
        'politicians',
        ['chamber', 'party'],
        postgresql_using='btree'
    )

    # Politicians table - composite index for state + chamber (geo analysis)
    op.create_index(
        'idx_politicians_state_chamber',
        'politicians',
        ['state', 'chamber'],
        postgresql_using='btree'
    )

    # Users table - index for email verification status
    op.execute("""
        CREATE INDEX idx_users_email_verified
        ON users (email)
        WHERE email_verified = true
    """)

    # Users table - index for active premium users
    op.execute("""
        CREATE INDEX idx_users_premium_active
        ON users (id, created_at)
        WHERE is_premium = true AND is_active = true
    """)

    print("✅ Performance indexes created successfully")


def downgrade() -> None:
    """Remove performance indexes"""

    # Drop trades indexes
    op.drop_index('idx_trades_politician_date', table_name='trades')
    op.drop_index('idx_trades_ticker_date', table_name='trades')
    op.drop_index('idx_trades_type_date', table_name='trades')
    op.drop_index('idx_trades_recent', table_name='trades')
    op.drop_index('idx_trades_large', table_name='trades')

    # Drop politicians indexes
    op.drop_index('idx_politicians_chamber_party', table_name='politicians')
    op.drop_index('idx_politicians_state_chamber', table_name='politicians')

    # Drop users indexes
    op.drop_index('idx_users_email_verified', table_name='users')
    op.drop_index('idx_users_premium_active', table_name='users')

    print("✅ Performance indexes removed")
