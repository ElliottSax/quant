"""
Real-Time Trading Signals API

WebSocket and REST endpoints for trading signal generation and streaming.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

from app.services.signal_generator import (
    SignalGenerator,
    TradingSignal,
    SignalType,
    get_signal_generator
)
from app.core.deps import get_current_user
from app.models.user import User


router = APIRouter(prefix="/signals", tags=["signals"])


class SignalRequest(BaseModel):
    """Request model for signal generation"""
    symbol: str
    price_data: List[float]
    volume_data: Optional[List[float]] = None
    use_ai: bool = True


class SignalResponse(BaseModel):
    """Response model for signals"""
    signal: TradingSignal
    generated_at: datetime


class WebSocketManager:
    """Manage WebSocket connections for real-time signals"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.signal_generator = get_signal_generator()

    async def connect(self, websocket: WebSocket, symbol: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = []
        self.active_connections[symbol].append(websocket)

    def disconnect(self, websocket: WebSocket, symbol: str):
        """Remove WebSocket connection"""
        if symbol in self.active_connections:
            if websocket in self.active_connections[symbol]:
                self.active_connections[symbol].remove(websocket)
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]

    async def broadcast_signal(self, symbol: str, signal: TradingSignal):
        """Broadcast signal to all connected clients for a symbol"""
        if symbol in self.active_connections:
            disconnected = []
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_json(signal.dict())
                except Exception:
                    disconnected.append(connection)

            # Clean up disconnected clients
            for conn in disconnected:
                self.disconnect(conn, symbol)

    async def generate_and_broadcast_signals(
        self,
        symbol: str,
        price_data: List[float],
        volume_data: Optional[List[float]] = None
    ):
        """Generate and broadcast signals"""
        try:
            signal = await self.signal_generator.generate_signal(
                symbol=symbol,
                price_data=price_data,
                volume_data=volume_data
            )
            await self.broadcast_signal(symbol, signal)
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}", exc_info=True)


# Global manager instance
manager = WebSocketManager()


@router.websocket("/ws/{symbol}")
async def websocket_signals(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for real-time trading signals

    Connect to receive live trading signals for a specific symbol:
    - ws://localhost:8000/api/v1/signals/ws/AAPL

    Signals are broadcast whenever new data is available
    """
    await manager.connect(websocket, symbol.upper())

    try:
        while True:
            # Wait for price updates from client
            data = await websocket.receive_json()

            if data.get("action") == "update_prices":
                price_data = data.get("prices", [])
                volume_data = data.get("volumes")

                if price_data:
                    # Generate and broadcast signal
                    await manager.generate_and_broadcast_signals(
                        symbol=symbol.upper(),
                        price_data=price_data,
                        volume_data=volume_data
                    )

    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol.upper())
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}", exc_info=True)
        manager.disconnect(websocket, symbol.upper())


@router.post("/generate", response_model=SignalResponse)
async def generate_signal(
    request: SignalRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate trading signal for given price data

    Analyzes historical price data and generates a comprehensive
    trading signal with technical indicators, risk assessment,
    and actionable recommendations.
    """
    generator = get_signal_generator()

    try:
        signal = await generator.generate_signal(
            symbol=request.symbol,
            price_data=request.price_data,
            volume_data=request.volume_data,
            use_ai=request.use_ai
        )

        return SignalResponse(
            signal=signal,
            generated_at=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating signal: {str(e)}"
        )


@router.get("/latest/{symbol}")
async def get_latest_signal(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the latest cached signal for a symbol

    Returns the most recently generated signal from cache if available
    """
    # This would integrate with a signal cache/database
    # For now, return a placeholder
    raise HTTPException(
        status_code=404,
        detail="No cached signal found. Use POST /generate to create new signal"
    )


@router.get("/history/{symbol}")
async def get_signal_history(
    symbol: str,
    limit: int = Query(default=100, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    signal_type: Optional[SignalType] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get historical signals for a symbol

    Returns past signals with optional filtering by:
    - Date range
    - Signal type (buy/sell/hold)
    - Limit
    """
    # This would query from a signals database table
    # Placeholder for now
    return {
        "symbol": symbol,
        "signals": [],
        "count": 0,
        "message": "Signal history feature coming soon"
    }


@router.get("/performance/{symbol}")
async def get_signal_performance(
    symbol: str,
    days: int = Query(default=30, le=365),
    current_user: User = Depends(get_current_user)
):
    """
    Get performance metrics for past signals

    Analyzes how accurate past signals were and calculates:
    - Win rate
    - Average return
    - Risk-adjusted returns
    - Signal accuracy by type
    """
    # This would analyze historical signals vs actual outcomes
    # Placeholder for now
    return {
        "symbol": symbol,
        "period_days": days,
        "metrics": {
            "total_signals": 0,
            "win_rate": 0.0,
            "avg_return": 0.0,
            "sharpe_ratio": 0.0
        },
        "message": "Performance tracking coming soon"
    }


@router.post("/backtest")
async def backtest_signals(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    initial_capital: float = 10000,
    current_user: User = Depends(get_current_user)
):
    """
    Backtest signal strategy on historical data

    Simulates trading based on generated signals and calculates
    performance metrics
    """
    # This will integrate with the backtesting engine
    return {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "message": "Backtesting integration coming soon"
    }


@router.get("/watchlist")
async def get_watchlist_signals(
    symbols: List[str] = Query(...),
    current_user: User = Depends(get_current_user)
):
    """
    Get signals for multiple symbols (watchlist)

    Returns current signals for a list of symbols
    """
    signals = []

    # This would fetch latest signals for all symbols
    # Placeholder for now
    for symbol in symbols[:10]:  # Limit to 10
        signals.append({
            "symbol": symbol,
            "message": "Generate signal first using POST /generate"
        })

    return {
        "signals": signals,
        "count": len(signals)
    }


@router.get("/market-overview")
async def get_market_overview(
    current_user: User = Depends(get_current_user)
):
    """
    Get market-wide signal overview

    Returns aggregated signal statistics across tracked symbols:
    - Number of buy/sell/hold signals
    - High confidence opportunities
    - Market sentiment score
    """
    return {
        "timestamp": datetime.utcnow(),
        "market_sentiment": "neutral",
        "signal_distribution": {
            "strong_buy": 0,
            "buy": 0,
            "hold": 0,
            "sell": 0,
            "strong_sell": 0
        },
        "high_confidence_opportunities": [],
        "message": "Market overview coming soon"
    }


@router.post("/alert")
async def create_signal_alert(
    symbol: str,
    signal_type: SignalType,
    min_confidence: float = 0.7,
    current_user: User = Depends(get_current_user)
):
    """
    Create alert for specific signal conditions

    Get notified when a signal matching your criteria is generated
    """
    # This would store alert preferences and trigger notifications
    return {
        "alert_id": "placeholder",
        "symbol": symbol,
        "signal_type": signal_type,
        "min_confidence": min_confidence,
        "status": "active",
        "message": "Alert system coming soon"
    }
