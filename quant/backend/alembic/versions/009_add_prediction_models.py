"""add prediction models

Revision ID: 009
Revises: 008
Create Date: 2026-02-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008_add_premium_features'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tables for stock predictions."""

    # StockPrediction table
    op.create_table(
        'stock_predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('symbol', sa.String(10), nullable=False, index=True),
        sa.Column('prediction_date', sa.DateTime(), nullable=False, index=True),
        sa.Column('horizon_days', sa.Integer(), nullable=False),
        sa.Column('model_type', sa.String(50), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('current_price', sa.Float(), nullable=False),
        sa.Column('predicted_price', sa.Float(), nullable=False),
        sa.Column('predicted_direction', sa.String(20), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('predicted_prices', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('actual_price', sa.Float(), nullable=True),
        sa.Column('actual_direction', sa.String(20), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_symbol_date', 'stock_predictions', ['symbol', 'prediction_date'])
    op.create_index('idx_model_type', 'stock_predictions', ['model_type'])
    op.create_index('idx_created_at', 'stock_predictions', ['created_at'])

    # TechnicalIndicators table
    op.create_table(
        'technical_indicators',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('symbol', sa.String(10), nullable=False, index=True),
        sa.Column('date', sa.DateTime(), nullable=False, index=True),
        sa.Column('open', sa.Float(), nullable=False),
        sa.Column('high', sa.Float(), nullable=False),
        sa.Column('low', sa.Float(), nullable=False),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('rsi', sa.Float(), nullable=True),
        sa.Column('macd', sa.Float(), nullable=True),
        sa.Column('macd_signal', sa.Float(), nullable=True),
        sa.Column('macd_hist', sa.Float(), nullable=True),
        sa.Column('stoch_k', sa.Float(), nullable=True),
        sa.Column('stoch_d', sa.Float(), nullable=True),
        sa.Column('sma_20', sa.Float(), nullable=True),
        sa.Column('sma_50', sa.Float(), nullable=True),
        sa.Column('sma_200', sa.Float(), nullable=True),
        sa.Column('ema_12', sa.Float(), nullable=True),
        sa.Column('ema_26', sa.Float(), nullable=True),
        sa.Column('adx', sa.Float(), nullable=True),
        sa.Column('bb_upper', sa.Float(), nullable=True),
        sa.Column('bb_middle', sa.Float(), nullable=True),
        sa.Column('bb_lower', sa.Float(), nullable=True),
        sa.Column('atr', sa.Float(), nullable=True),
        sa.Column('obv', sa.Float(), nullable=True),
        sa.Column('vwap', sa.Float(), nullable=True),
        sa.Column('other_indicators', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_symbol_date_unique', 'technical_indicators', ['symbol', 'date'], unique=True)

    # TradingSignal table
    op.create_table(
        'trading_signals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('symbol', sa.String(10), nullable=False, index=True),
        sa.Column('signal_type', sa.String(20), nullable=False),
        sa.Column('signal_date', sa.DateTime(), nullable=False, index=True),
        sa.Column('strategy_name', sa.String(100), nullable=False),
        sa.Column('model_type', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('strength', sa.String(20), nullable=True),
        sa.Column('current_price', sa.Float(), nullable=False),
        sa.Column('target_price', sa.Float(), nullable=True),
        sa.Column('stop_loss', sa.Float(), nullable=True),
        sa.Column('reasoning', sa.String(500), nullable=True),
        sa.Column('technical_signals', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('patterns_detected', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('executed', sa.Boolean(), nullable=False, default=False),
        sa.Column('execution_price', sa.Float(), nullable=True),
        sa.Column('outcome', sa.String(20), nullable=True),
        sa.Column('profit_loss', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_symbol_signal_date', 'trading_signals', ['symbol', 'signal_date'])
    op.create_index('idx_signal_type', 'trading_signals', ['signal_type'])
    op.create_index('idx_strategy', 'trading_signals', ['strategy_name'])

    # PatternDetection table
    op.create_table(
        'pattern_detections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('symbol', sa.String(10), nullable=False, index=True),
        sa.Column('detection_date', sa.DateTime(), nullable=False, index=True),
        sa.Column('pattern_type', sa.String(50), nullable=False),
        sa.Column('pattern_name', sa.String(100), nullable=False),
        sa.Column('pattern_category', sa.String(50), nullable=True),
        sa.Column('strength', sa.String(20), nullable=True),
        sa.Column('direction', sa.String(20), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('price_at_detection', sa.Float(), nullable=False),
        sa.Column('pattern_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('price_after_1d', sa.Float(), nullable=True),
        sa.Column('price_after_5d', sa.Float(), nullable=True),
        sa.Column('price_after_10d', sa.Float(), nullable=True),
        sa.Column('pattern_success', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_pattern_type', 'pattern_detections', ['pattern_type'])
    op.create_index('idx_pattern_date', 'pattern_detections', ['symbol', 'detection_date'])

    # ModelPerformance table
    op.create_table(
        'model_performance',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('model_type', sa.String(50), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('evaluation_date', sa.DateTime(), nullable=False, index=True),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('accuracy', sa.Float(), nullable=False),
        sa.Column('precision', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('total_predictions', sa.Integer(), nullable=False),
        sa.Column('correct_predictions', sa.Integer(), nullable=False),
        sa.Column('direction_accuracy', sa.Float(), nullable=True),
        sa.Column('metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_model_eval', 'model_performance', ['model_type', 'evaluation_date'])


def downgrade() -> None:
    """Drop prediction tables."""
    op.drop_table('model_performance')
    op.drop_table('pattern_detections')
    op.drop_table('trading_signals')
    op.drop_table('technical_indicators')
    op.drop_table('stock_predictions')
