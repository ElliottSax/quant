"""Add data_source table

Revision ID: 007_add_data_source_table
Revises: 006_add_performance_indexes
Create Date: 2024-02-03 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_add_data_source_table'
down_revision = '006_add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create data_sources table."""
    op.create_table(
        'data_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('run_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('records_found', sa.Integer(), nullable=True, default=0),
        sa.Column('records_imported', sa.Integer(), nullable=True, default=0),
        sa.Column('records_skipped', sa.Integer(), nullable=True, default=0),
        sa.Column('records_invalid', sa.Integer(), nullable=True, default=0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('source_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(
        op.f('ix_data_sources_source_type'),
        'data_sources',
        ['source_type'],
        unique=False
    )
    op.create_index(
        op.f('ix_data_sources_run_date'),
        'data_sources',
        ['run_date'],
        unique=False
    )
    op.create_index(
        op.f('ix_data_sources_status'),
        'data_sources',
        ['status'],
        unique=False
    )


def downgrade() -> None:
    """Drop data_sources table."""
    op.drop_index(op.f('ix_data_sources_status'), table_name='data_sources')
    op.drop_index(op.f('ix_data_sources_run_date'), table_name='data_sources')
    op.drop_index(op.f('ix_data_sources_source_type'), table_name='data_sources')
    op.drop_table('data_sources')
