"""add analytics tables

Revision ID: add_analytics_20260203
Revises:
Create Date: 2026-02-03

Add tables for advanced analytics:
- options_analysis_cache
- sentiment_analysis_cache
- pattern_recognition_results
- correlation_analysis_cache
- predictive_model_results
- risk_score_cache
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_analytics_20260203'
down_revision = '010_add_hybrid_model_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Options Analysis Cache
    op.create_table(
        'options_analysis_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ticker', sa.String(10), nullable=False, index=True),
        sa.Column('analysis_date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('total_gamma', sa.Float),
        sa.Column('net_gamma', sa.Float),
        sa.Column('gamma_flip_price', sa.Float),
        sa.Column('market_stance', sa.String(20)),
        sa.Column('call_volume', sa.Integer),
        sa.Column('put_volume', sa.Integer),
        sa.Column('call_put_ratio', sa.Float),
        sa.Column('net_premium_flow', sa.Float),
        sa.Column('flow_sentiment', sa.String(20)),
        sa.Column('overall_sentiment', sa.String(20)),
        sa.Column('confidence', sa.Float),
        sa.Column('full_analysis', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_options_ticker_date', 'options_analysis_cache', ['ticker', 'analysis_date'])

    # Sentiment Analysis Cache
    op.create_table(
        'sentiment_analysis_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('politician_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('politicians.id', ondelete='CASCADE'), index=True),
        sa.Column('ticker', sa.String(10), index=True),
        sa.Column('analysis_date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('overall_score', sa.Float, nullable=False),
        sa.Column('overall_category', sa.String(20), nullable=False),
        sa.Column('confidence', sa.Float, nullable=False),
        sa.Column('items_analyzed', sa.Integer, nullable=False),
        sa.Column('positive_count', sa.Integer, nullable=False),
        sa.Column('negative_count', sa.Integer, nullable=False),
        sa.Column('neutral_count', sa.Integer, nullable=False),
        sa.Column('source_breakdown', postgresql.JSONB, nullable=False),
        sa.Column('trend_24h', sa.Float),
        sa.Column('full_analysis', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_sentiment_politician_date', 'sentiment_analysis_cache', ['politician_id', 'analysis_date'])
    op.create_index('idx_sentiment_ticker_date', 'sentiment_analysis_cache', ['ticker', 'analysis_date'])

    # Pattern Recognition Results
    op.create_table(
        'pattern_recognition_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('pattern_type', sa.String(50), nullable=False, index=True),
        sa.Column('politician_ids', postgresql.JSONB, nullable=False),
        sa.Column('pattern_data', postgresql.JSONB, nullable=False),
        sa.Column('confidence', sa.Float, nullable=False),
        sa.Column('significance', sa.Float),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_pattern_type_date', 'pattern_recognition_results', ['pattern_type', 'analysis_date'])

    # Correlation Analysis Cache
    op.create_table(
        'correlation_analysis_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('correlation_type', sa.String(50), nullable=False, index=True),
        sa.Column('entity1_id', sa.String(100), index=True),
        sa.Column('entity2_id', sa.String(100), index=True),
        sa.Column('correlation', sa.Float, nullable=False),
        sa.Column('p_value', sa.Float),
        sa.Column('lookback_days', sa.Integer, nullable=False),
        sa.Column('metrics', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_correlation_type_date', 'correlation_analysis_cache', ['correlation_type', 'analysis_date'])
    op.create_index('idx_correlation_entities', 'correlation_analysis_cache', ['entity1_id', 'entity2_id'])

    # Predictive Model Results
    op.create_table(
        'predictive_model_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('politician_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('politicians.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('model_name', sa.String(100), nullable=False, index=True),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('prediction_date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('prediction_type', sa.String(50), nullable=False),
        sa.Column('predicted_value', sa.Float, nullable=False),
        sa.Column('confidence', sa.Float, nullable=False),
        sa.Column('forecast_days', sa.Integer),
        sa.Column('target_date', sa.Date),
        sa.Column('features', postgresql.JSONB),
        sa.Column('model_accuracy', sa.Float),
        sa.Column('model_metrics', postgresql.JSONB),
        sa.Column('explanation', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_prediction_politician_date', 'predictive_model_results', ['politician_id', 'prediction_date'])
    op.create_index('idx_prediction_model_date', 'predictive_model_results', ['model_name', 'prediction_date'])

    # Risk Score Cache
    op.create_table(
        'risk_score_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('politician_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('politicians.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('analysis_date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('overall_risk_score', sa.Float, nullable=False),
        sa.Column('volatility_score', sa.Float, nullable=False),
        sa.Column('consistency_score', sa.Float, nullable=False),
        sa.Column('timing_risk_score', sa.Float, nullable=False),
        sa.Column('risk_category', sa.String(20), nullable=False),
        sa.Column('risk_factors', postgresql.JSONB, nullable=False),
        sa.Column('explanation', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_risk_politician_date', 'risk_score_cache', ['politician_id', 'analysis_date'])
    op.create_index('idx_risk_score', 'risk_score_cache', ['overall_risk_score'])


def downgrade() -> None:
    op.drop_table('risk_score_cache')
    op.drop_table('predictive_model_results')
    op.drop_table('correlation_analysis_cache')
    op.drop_table('pattern_recognition_results')
    op.drop_table('sentiment_analysis_cache')
    op.drop_table('options_analysis_cache')
