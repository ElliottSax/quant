"""Add pattern detection tables

Revision ID: 003
Revises: 002
Create Date: 2025-11-13 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create pattern detection tables."""
    # Create patterns table
    op.create_table(
        'patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('pattern_id', sa.String(100), nullable=False, unique=True),
        sa.Column('pattern_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('ticker', sa.String(10), nullable=True),
        sa.Column('sector', sa.String(100), nullable=True),
        sa.Column('market_cap', sa.String(20), nullable=True),
        sa.Column('cycle_length_days', sa.Integer(), nullable=False),
        sa.Column('frequency', sa.String(20), nullable=True),
        sa.Column('next_occurrence', sa.Date(), nullable=True),
        sa.Column('window_start_day', sa.Integer(), nullable=True),
        sa.Column('window_end_day', sa.Integer(), nullable=True),
        sa.Column('validation_metrics', postgresql.JSONB(), nullable=False),
        sa.Column('reliability_score', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('first_detected', sa.Date(), nullable=True),
        sa.Column('last_validated', sa.Date(), nullable=False),
        sa.Column('economic_rationale', sa.Text(), nullable=True),
        sa.Column('risk_factors', postgresql.JSONB(), nullable=True),
        sa.Column('politician_correlation', sa.Float(), nullable=True),
        sa.Column('recent_politician_activity', postgresql.JSONB(), nullable=True),
        sa.Column(
            'detected_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column('detector_version', sa.String(20), nullable=False, server_default='1.0.0'),
        sa.Column('parameters', postgresql.JSONB(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        # Constraints
        sa.CheckConstraint(
            "pattern_type IN ('seasonal', 'calendar', 'cycle', 'regime', 'behavioral', 'politician', 'earnings', 'economic')",
            name='valid_pattern_type',
        ),
        sa.CheckConstraint(
            "frequency IS NULL OR frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'annual')",
            name='valid_frequency',
        ),
        sa.CheckConstraint(
            'reliability_score >= 0 AND reliability_score <= 100',
            name='valid_reliability_score',
        ),
        sa.CheckConstraint(
            'confidence >= 0 AND confidence <= 100',
            name='valid_confidence',
        ),
        sa.CheckConstraint(
            'cycle_length_days > 0',
            name='valid_cycle_length',
        ),
        sa.CheckConstraint(
            'politician_correlation IS NULL OR (politician_correlation >= -1 AND politician_correlation <= 1)',
            name='valid_correlation',
        ),
    )

    # Create indexes for patterns table
    op.create_index('ix_patterns_pattern_id', 'patterns', ['pattern_id'], unique=True)
    op.create_index('ix_patterns_pattern_type', 'patterns', ['pattern_type'])
    op.create_index('ix_patterns_ticker', 'patterns', ['ticker'])
    op.create_index('ix_patterns_reliability_score', 'patterns', ['reliability_score'])
    op.create_index('ix_patterns_next_occurrence', 'patterns', ['next_occurrence'])
    op.create_index('ix_patterns_is_active', 'patterns', ['is_active'])
    op.create_index(
        'idx_active_patterns',
        'patterns',
        ['is_active', 'pattern_type', 'ticker'],
    )
    op.create_index(
        'idx_upcoming_patterns',
        'patterns',
        ['next_occurrence', 'is_active'],
        postgresql_where=sa.text('is_active = true'),
    )
    op.create_index(
        'idx_reliable_patterns',
        'patterns',
        ['reliability_score', 'is_active'],
        postgresql_where=sa.text('reliability_score >= 70'),
    )

    # Create pattern_occurrences table
    op.create_table(
        'pattern_occurrences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'pattern_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('patterns.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('return_pct', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('volume_change', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        # Constraints
        sa.CheckConstraint(
            'confidence >= 0 AND confidence <= 100',
            name='valid_occurrence_confidence',
        ),
        sa.CheckConstraint(
            'end_date >= start_date',
            name='valid_date_range',
        ),
    )

    # Create indexes for pattern_occurrences table
    op.create_index('ix_pattern_occurrences_pattern_id', 'pattern_occurrences', ['pattern_id'])
    op.create_index('ix_pattern_occurrences_start_date', 'pattern_occurrences', ['start_date'])
    op.create_index('ix_pattern_occurrences_end_date', 'pattern_occurrences', ['end_date'])
    op.create_index(
        'idx_unique_occurrence',
        'pattern_occurrences',
        ['pattern_id', 'start_date', 'end_date'],
        unique=True,
    )
    op.create_index(
        'idx_recent_occurrences',
        'pattern_occurrences',
        ['pattern_id', 'end_date'],
    )


def downgrade() -> None:
    """Drop pattern detection tables."""
    op.drop_table('pattern_occurrences')
    op.drop_table('patterns')
