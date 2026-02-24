"""
Secured stock prediction API endpoints with authentication and rate limiting.

This is a secured version of the prediction endpoints that includes:
- Authentication (required for all endpoints)
- Rate limiting (per-user, tier-based)
- Input validation and sanitization
- Proper error handling

To use these endpoints instead of the original ones, update app/api/v1/__init__.py
to import from prediction_secure instead of prediction.
"""

import logging
import re
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from pydantic import BaseModel, Field, field_validator
import pandas as pd

from app.services.market_data import MarketDataClient
from app.services.technical_analysis import IndicatorCalculator, PatternDetector
from app.core.deps import get_redis_client, get_current_user, get_current_user_optional
from app.core.rate_limiting import check_prediction_rate_limit
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prediction", tags=["prediction"])


# Input validation helpers
def validate_stock_symbol(symbol: str) -> str:
    """Validate and sanitize stock ticker symbol."""
    # Remove whitespace and convert to uppercase
    symbol = symbol.strip().upper()

    # Check format (letters and optionally dots/hyphens for international symbols)
    if not re.match(r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$', symbol):
        raise ValueError(f"Invalid stock symbol format: {symbol}")

    return symbol


def validate_period(period: str) -> str:
    """Validate period parameter."""
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    if period not in valid_periods:
        raise ValueError(f"Invalid period. Must be one of: {', '.join(valid_periods)}")
    return period


def validate_interval(interval: str) -> str:
    """Validate interval parameter."""
    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    if interval not in valid_intervals:
        raise ValueError(f"Invalid interval. Must be one of: {', '.join(valid_intervals)}")
    return interval


# Request/Response Models with validation
class PredictionRequest(BaseModel):
    """Request model for stock prediction with validation."""
    symbol: str = Field(..., description="Stock ticker symbol", min_length=1, max_length=10)
    period: str = Field("1y", description="Historical period for analysis")
    horizon: int = Field(5, ge=1, le=30, description="Prediction horizon in days")

    @field_validator('symbol')
    @classmethod
    def validate_symbol_field(cls, v: str) -> str:
        return validate_stock_symbol(v)

    @field_validator('period')
    @classmethod
    def validate_period_field(cls, v: str) -> str:
        return validate_period(v)


class PredictionResponse(BaseModel):
    """Response model for stock prediction."""
    symbol: str
    current_price: float
    predicted_prices: List[float]
    predicted_direction: str  # 'UP', 'DOWN', 'NEUTRAL'
    confidence: float
    technical_signals: dict
    recommendation: str  # 'BUY', 'SELL', 'HOLD'
    timestamp: str


class IndicatorRequest(BaseModel):
    """Request model for technical indicators with validation."""
    symbol: str = Field(..., min_length=1, max_length=10)
    period: str = Field("1y")
    interval: str = Field("1d")

    @field_validator('symbol')
    @classmethod
    def validate_symbol_field(cls, v: str) -> str:
        return validate_stock_symbol(v)

    @field_validator('period')
    @classmethod
    def validate_period_field(cls, v: str) -> str:
        return validate_period(v)

    @field_validator('interval')
    @classmethod
    def validate_interval_field(cls, v: str) -> str:
        return validate_interval(v)


class IndicatorResponse(BaseModel):
    """Response model for technical indicators."""
    symbol: str
    timestamp: str
    indicators: dict
    signals: dict


class PatternScanRequest(BaseModel):
    """Request model for pattern scanning with validation."""
    symbols: List[str] = Field(..., min_items=1, max_items=50, description="List of stock symbols (max 50)")
    pattern_types: Optional[List[str]] = None

    @field_validator('symbols')
    @classmethod
    def validate_symbols_field(cls, v: List[str]) -> List[str]:
        return [validate_stock_symbol(symbol) for symbol in v]


class PatternScanResponse(BaseModel):
    """Response model for pattern scanning."""
    timestamp: str
    results: dict  # {symbol: [patterns]}
    total_patterns_found: int


# Secured endpoints with authentication and rate limiting
@router.post("/predict", response_model=PredictionResponse)
async def predict_stock(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    redis_client = Depends(get_redis_client),
    _rate_limit = Depends(check_prediction_rate_limit)
):
    """
    Get ML-powered stock price predictions (AUTHENTICATED).

    Requires authentication. Rate limited based on user tier:
    - Free: 20 requests/minute, 500/hour
    - Premium: 200 requests/minute, 10,000/hour

    This endpoint:
    1. Fetches historical data
    2. Calculates technical indicators
    3. Runs ensemble ML models (LSTM, XGBoost, etc.)
    4. Returns prediction with confidence score

    **Note**: ML models will be implemented in Phase 2.
    """
    try:
        # Initialize clients
        market_data = MarketDataClient(redis_client)
        indicator_calc = IndicatorCalculator()

        # Fetch historical data
        df = await market_data.get_historical_data(
            request.symbol,
            period=request.period,
            interval="1d"
        )

        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for {request.symbol}"
            )

        # Calculate indicators
        indicators = indicator_calc.calculate_all(df)

        # Get current price
        current_price = float(df['Close'].iloc[-1])

        # TODO: Implement actual ML prediction models
        # For now, return placeholder based on technical signals
        signals = indicators.get('signals', {})
        overall_signal = signals.get('overall', 'HOLD')

        # Placeholder prediction (replace with actual ML model)
        if overall_signal == 'BUY':
            predicted_direction = 'UP'
            predicted_prices = [current_price * (1 + 0.01 * i) for i in range(1, request.horizon + 1)]
            confidence = 0.65
        elif overall_signal == 'SELL':
            predicted_direction = 'DOWN'
            predicted_prices = [current_price * (1 - 0.01 * i) for i in range(1, request.horizon + 1)]
            confidence = 0.65
        else:
            predicted_direction = 'NEUTRAL'
            predicted_prices = [current_price] * request.horizon
            confidence = 0.50

        await market_data.close()

        logger.info(f"Prediction generated for {request.symbol} by user {current_user.id}")

        return PredictionResponse(
            symbol=request.symbol,
            current_price=current_price,
            predicted_prices=predicted_prices,
            predicted_direction=predicted_direction,
            confidence=confidence,
            technical_signals=signals,
            recommendation=overall_signal,
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error for {request.symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating prediction"
        )


@router.post("/indicators", response_model=IndicatorResponse)
async def calculate_indicators(
    request: IndicatorRequest,
    current_user: User = Depends(get_current_user),
    redis_client = Depends(get_redis_client),
    _rate_limit = Depends(check_prediction_rate_limit)
):
    """
    Calculate comprehensive technical indicators for a stock (AUTHENTICATED).

    Requires authentication. Rate limited based on user tier.

    Returns 50+ indicators across 4 categories:
    - Momentum: RSI, Stochastic, Williams %R, ROC, MFI
    - Trend: SMA, EMA, MACD, ADX, Aroon
    - Volatility: Bollinger Bands, ATR, Keltner Channels
    - Volume: OBV, CMF, VWAP, PVT
    """
    try:
        market_data = MarketDataClient(redis_client)
        indicator_calc = IndicatorCalculator()

        # Fetch data
        df = await market_data.get_historical_data(
            request.symbol,
            period=request.period,
            interval=request.interval
        )

        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for {request.symbol}"
            )

        # Calculate indicators
        indicators = indicator_calc.calculate_all(df)

        await market_data.close()

        logger.info(f"Indicators calculated for {request.symbol} by user {current_user.id}")

        return IndicatorResponse(
            symbol=request.symbol,
            timestamp=df.index[-1].isoformat(),
            indicators=indicators.get('current', {}),
            signals=indicators.get('signals', {})
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Indicator calculation error for {request.symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while calculating indicators"
        )


@router.post("/patterns/scan", response_model=PatternScanResponse)
async def scan_patterns(
    request: PatternScanRequest,
    current_user: User = Depends(get_current_user),
    redis_client = Depends(get_redis_client),
    _rate_limit = Depends(check_prediction_rate_limit)
):
    """
    Scan multiple stocks for candlestick patterns (AUTHENTICATED).

    Requires authentication. Rate limited. Maximum 50 symbols per request.

    Detects 60+ patterns including:
    - Reversal: Hammer, Shooting Star, Engulfing, Morning/Evening Star
    - Continuation: Three White Soldiers, Three Black Crows
    - Doji: Dragonfly, Gravestone, Long-legged
    """
    try:
        market_data = MarketDataClient(redis_client)
        pattern_detector = PatternDetector()

        # Fetch data for all symbols
        data_dict = {}
        for symbol in request.symbols:
            try:
                df = await market_data.get_historical_data(symbol, period="1mo", interval="1d")
                if not df.empty:
                    data_dict[symbol] = df
            except Exception as e:
                logger.warning(f"Failed to fetch data for {symbol}: {e}")
                continue

        # Scan for patterns
        results = pattern_detector.scan_multiple_symbols(
            data_dict,
            pattern_filter=request.pattern_types
        )

        # Count total patterns
        total_patterns = sum(len(patterns) for patterns in results.values())

        await market_data.close()

        logger.info(f"Pattern scan completed for {len(request.symbols)} symbols by user {current_user.id}")

        return PatternScanResponse(
            timestamp=datetime.utcnow().isoformat(),
            results=results,
            total_patterns_found=total_patterns
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Pattern scan error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while scanning patterns"
        )


@router.get("/signals/daily")
async def get_daily_signals(
    symbols: List[str] = Query(..., max_items=50, description="List of stock symbols (max 50)"),
    current_user: User = Depends(get_current_user),
    redis_client = Depends(get_redis_client),
    _rate_limit = Depends(check_prediction_rate_limit)
):
    """
    Get daily trading signals for multiple stocks (AUTHENTICATED).

    Requires authentication. Rate limited. Maximum 50 symbols per request.

    Returns buy/sell/hold recommendations based on:
    - Technical indicators
    - Candlestick patterns
    - ML predictions (when implemented)
    """
    try:
        # Validate symbols
        validated_symbols = [validate_stock_symbol(s) for s in symbols[:50]]

        market_data = MarketDataClient(redis_client)
        indicator_calc = IndicatorCalculator()
        pattern_detector = PatternDetector()

        results = []

        for symbol in validated_symbols:
            try:
                # Fetch data
                df = await market_data.get_historical_data(symbol, period="3mo", interval="1d")
                if df.empty:
                    continue

                # Calculate indicators
                indicators = indicator_calc.calculate_all(df)

                # Detect patterns
                patterns = pattern_detector.detect_all_patterns(df)

                # Get quote
                quote = await market_data.get_quote(symbol)

                results.append({
                    'symbol': symbol,
                    'price': quote.get('price'),
                    'change_percent': quote.get('change_percent'),
                    'signal': indicators['signals'].get('overall', 'HOLD'),
                    'technical_signals': indicators['signals'],
                    'patterns': patterns['current'],
                    'rsi': indicators['current'].get('rsi'),
                    'volume': quote.get('volume')
                })

            except Exception as e:
                logger.warning(f"Failed to process {symbol}: {e}")
                continue

        await market_data.close()

        logger.info(f"Daily signals generated for {len(results)} symbols by user {current_user.id}")

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'signals': results,
            'total_analyzed': len(results)
        }

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Daily signals error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating signals"
        )


@router.post("/batch")
async def batch_predict(
    symbols: List[str] = Query(..., max_items=50, description="List of stock symbols (max 50)"),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
    redis_client = Depends(get_redis_client),
    _rate_limit = Depends(check_prediction_rate_limit)
):
    """
    Get predictions for multiple stocks in batch (AUTHENTICATED).

    Requires authentication. Rate limited. Maximum 50 symbols per request.
    Processes up to 50 symbols at once.
    """
    try:
        # Validate symbols
        validated_symbols = [validate_stock_symbol(s) for s in symbols[:50]]

        results = []

        for symbol in validated_symbols:
            try:
                request = PredictionRequest(symbol=symbol)
                prediction = await predict_stock(request, current_user, redis_client, None)
                results.append(prediction.dict())
            except Exception as e:
                logger.warning(f"Batch prediction failed for {symbol}: {e}")
                results.append({
                    'symbol': symbol,
                    'error': str(e)
                })

        logger.info(f"Batch prediction completed for {len(results)} symbols by user {current_user.id}")

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'predictions': results,
            'total_processed': len(results)
        }

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Batch prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during batch prediction"
        )
