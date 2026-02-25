"""
Stock prediction API endpoints.

Provides:
- /predict/{symbol} - Get ML predictions for a stock
- /predict/batch - Batch predictions for multiple stocks
- /indicators/{symbol} - Calculate technical indicators
- /patterns/scan - Scan for candlestick patterns
- /signals/daily - Get daily trading signals
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.market_data import MarketDataClient
from app.services.technical_analysis import IndicatorCalculator, PatternDetector
from app.core.deps import get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prediction", tags=["prediction"])


# Request/Response Models
class PredictionRequest(BaseModel):
    """Request model for stock prediction."""
    symbol: str = Field(..., description="Stock ticker symbol")
    period: str = Field("1y", description="Historical period for analysis")
    horizon: int = Field(5, ge=1, le=30, description="Prediction horizon in days")


class PredictionResponse(BaseModel):
    """Response model for stock prediction."""
    symbol: str
    current_price: float
    predicted_prices: List[float]
    predicted_direction: str  # 'UP', 'DOWN', 'NEUTRAL'
    confidence: float
    technical_signals: dict
    recommendation: str  # 'BUY', 'SELL', 'HOLD'


class IndicatorRequest(BaseModel):
    """Request model for technical indicators."""
    symbol: str
    period: str = "1y"
    interval: str = "1d"


class IndicatorResponse(BaseModel):
    """Response model for technical indicators."""
    symbol: str
    timestamp: str
    indicators: dict
    signals: dict


class PatternScanRequest(BaseModel):
    """Request model for pattern scanning."""
    symbols: List[str] = Field(..., max_items=100)
    pattern_types: Optional[List[str]] = None


class PatternScanResponse(BaseModel):
    """Response model for pattern scanning."""
    timestamp: str
    results: dict  # {symbol: [patterns]}
    total_patterns_found: int


# Endpoints
@router.post("/predict", response_model=PredictionResponse)
async def predict_stock(
    request: PredictionRequest,
    redis_client = Depends(get_redis_client)
):
    """
    Get ML-powered stock price predictions.

    This endpoint:
    1. Fetches historical data
    2. Calculates technical indicators
    3. Runs ensemble ML models (LSTM, XGBoost, etc.)
    4. Returns prediction with confidence score

    **Note**: This is a placeholder. Implement ML models in Phase 3.
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
            raise HTTPException(status_code=404, detail=f"No data found for {request.symbol}")

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

        return PredictionResponse(
            symbol=request.symbol,
            current_price=current_price,
            predicted_prices=predicted_prices,
            predicted_direction=predicted_direction,
            confidence=confidence,
            technical_signals=signals,
            recommendation=overall_signal
        )

    except Exception as e:
        logger.error(f"Prediction error for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/indicators", response_model=IndicatorResponse)
async def calculate_indicators(
    request: IndicatorRequest,
    redis_client = Depends(get_redis_client)
):
    """
    Calculate comprehensive technical indicators for a stock.

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
            raise HTTPException(status_code=404, detail=f"No data found for {request.symbol}")

        # Calculate indicators
        indicators = indicator_calc.calculate_all(df)

        await market_data.close()

        return IndicatorResponse(
            symbol=request.symbol,
            timestamp=df.index[-1].isoformat(),
            indicators=indicators.get('current', {}),
            signals=indicators.get('signals', {})
        )

    except Exception as e:
        logger.error(f"Indicator calculation error for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/patterns/scan", response_model=PatternScanResponse)
async def scan_patterns(
    request: PatternScanRequest,
    redis_client = Depends(get_redis_client)
):
    """
    Scan multiple stocks for candlestick patterns.

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

        return PatternScanResponse(
            timestamp=pd.Timestamp.now().isoformat(),
            results=results,
            total_patterns_found=total_patterns
        )

    except Exception as e:
        logger.error(f"Pattern scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/daily")
async def get_daily_signals(
    symbols: List[str] = Query(..., description="List of stock symbols"),
    redis_client = Depends(get_redis_client)
):
    """
    Get daily trading signals for multiple stocks.

    Returns buy/sell/hold recommendations based on:
    - Technical indicators
    - Candlestick patterns
    - ML predictions (when implemented)
    """
    try:
        market_data = MarketDataClient(redis_client)
        indicator_calc = IndicatorCalculator()
        pattern_detector = PatternDetector()

        results = []

        for symbol in symbols[:50]:  # Limit to 50 symbols
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

        return {
            'timestamp': pd.Timestamp.now().isoformat(),
            'signals': results,
            'total_analyzed': len(results)
        }

    except Exception as e:
        logger.error(f"Daily signals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Batch prediction endpoint
@router.post("/batch")
async def batch_predict(
    symbols: List[str] = Query(..., max_items=50),
    background_tasks: BackgroundTasks = None,
    redis_client = Depends(get_redis_client)
):
    """
    Get predictions for multiple stocks in batch.

    Processes up to 50 symbols at once.
    Use background tasks for larger batches.
    """
    results = []

    for symbol in symbols:
        try:
            request = PredictionRequest(symbol=symbol)
            prediction = await predict_stock(request, redis_client)
            results.append(prediction.dict())
        except Exception as e:
            logger.warning(f"Batch prediction failed for {symbol}: {e}")
            results.append({
                'symbol': symbol,
                'error': str(e)
            })

    return {
        'timestamp': pd.Timestamp.now().isoformat(),
        'predictions': results,
        'total_processed': len(results)
    }


# Import pandas for timestamp
import pandas as pd
