"""
Performance metrics and monitoring for backtesting API
Tracks usage, performance, and errors
"""

import time
import logging
from typing import Dict, Optional
from datetime import datetime
from functools import wraps
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and tracks API metrics"""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.strategy_usage = defaultdict(int)
        self.symbol_usage = defaultdict(int)
        self.yahoo_finance_calls = 0
        self.yahoo_finance_failures = 0
    
    def record_request(self, endpoint: str):
        """Record an API request"""
        self.request_counts[endpoint] += 1
    
    def record_error(self, endpoint: str, error_type: str):
        """Record an API error"""
        error_key = f"{endpoint}:{error_type}"
        self.error_counts[error_key] += 1
    
    def record_response_time(self, endpoint: str, duration_ms: float):
        """Record response time"""
        self.response_times[endpoint].append(duration_ms)
        
        # Keep only last 100 measurements per endpoint
        if len(self.response_times[endpoint]) > 100:
            self.response_times[endpoint].pop(0)
    
    def record_strategy_use(self, strategy: str):
        """Track strategy usage"""
        self.strategy_usage[strategy] += 1
    
    def record_symbol_use(self, symbol: str):
        """Track symbol usage"""
        self.symbol_usage[symbol] += 1
    
    def record_yahoo_finance_call(self, success: bool = True):
        """Track Yahoo Finance API calls"""
        self.yahoo_finance_calls += 1
        if not success:
            self.yahoo_finance_failures += 1
    
    def get_summary(self) -> Dict:
        """Get metrics summary"""
        avg_response_times = {}
        for endpoint, times in self.response_times.items():
            if times:
                avg_response_times[endpoint] = sum(times) / len(times)
        
        return {
            "total_requests": sum(self.request_counts.values()),
            "requests_by_endpoint": dict(self.request_counts),
            "total_errors": sum(self.error_counts.values()),
            "errors_by_type": dict(self.error_counts),
            "avg_response_times_ms": avg_response_times,
            "top_strategies": dict(sorted(
                self.strategy_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            "top_symbols": dict(sorted(
                self.symbol_usage.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            "yahoo_finance": {
                "total_calls": self.yahoo_finance_calls,
                "failures": self.yahoo_finance_failures,
                "success_rate": (
                    (self.yahoo_finance_calls - self.yahoo_finance_failures) / 
                    self.yahoo_finance_calls * 100
                ) if self.yahoo_finance_calls > 0 else 0
            }
        }
    
    def log_summary(self):
        """Log metrics summary"""
        summary = self.get_summary()
        logger.info(f"Metrics Summary: {json.dumps(summary, indent=2)}")


# Global metrics collector
metrics = MetricsCollector()


def track_performance(endpoint_name: str):
    """Decorator to track endpoint performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            metrics.record_request(endpoint_name)
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                metrics.record_response_time(endpoint_name, duration_ms)
                
                logger.info(
                    f"{endpoint_name} completed in {duration_ms:.2f}ms",
                    extra={
                        "endpoint": endpoint_name,
                        "duration_ms": duration_ms,
                        "status": "success"
                    }
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                error_type = type(e).__name__
                metrics.record_error(endpoint_name, error_type)
                
                logger.error(
                    f"{endpoint_name} failed after {duration_ms:.2f}ms: {str(e)}",
                    extra={
                        "endpoint": endpoint_name,
                        "duration_ms": duration_ms,
                        "error_type": error_type,
                        "error_message": str(e),
                        "status": "error"
                    },
                    exc_info=True
                )
                
                raise
        
        return wrapper
    return decorator


def log_backtest_request(symbol: str, strategy: str, duration_days: int):
    """Log backtest request details"""
    logger.info(
        f"Backtest requested: {symbol} | {strategy} | {duration_days} days",
        extra={
            "event_type": "backtest_request",
            "symbol": symbol,
            "strategy": strategy,
            "duration_days": duration_days,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    # Track in metrics
    metrics.record_strategy_use(strategy)
    metrics.record_symbol_use(symbol)


def log_data_fetch(symbol: str, start_date: str, end_date: str, success: bool, data_points: int = 0):
    """Log market data fetch attempt"""
    logger.info(
        f"Data fetch for {symbol}: {'SUCCESS' if success else 'FAILED'} ({data_points} points)",
        extra={
            "event_type": "data_fetch",
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "success": success,
            "data_points": data_points,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    metrics.record_yahoo_finance_call(success)
