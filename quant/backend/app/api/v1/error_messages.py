"""
Comprehensive error messages for backtesting API
Provides helpful, actionable error messages for users
"""

from typing import Dict, List


class BacktestErrorMessages:
    """Centralized error messages with helpful guidance"""
    
    # Date validation errors
    DATE_ORDER_ERROR = {
        "message": "End date must be after start date",
        "suggestion": "Check your date range and ensure start_date < end_date",
        "example": {
            "start_date": "2025-01-01T00:00:00",
            "end_date": "2025-12-31T23:59:59"
        }
    }
    
    DEMO_DURATION_ERROR = {
        "message": "Demo mode limited to 1 year backtests",
        "suggestion": "Reduce your date range to 365 days or less, or upgrade to premium for longer backtests",
        "premium_benefits": [
            "Up to 10 years historical data",
            "Advanced strategies",
            "Real-time execution"
        ]
    }
    
    MAX_DURATION_ERROR = {
        "message": "Maximum backtest duration is 10 years",
        "suggestion": "Reduce your date range to 3650 days or less"
    }
    
    FUTURE_DATE_ERROR = {
        "message": "Cannot backtest future dates",
        "suggestion": "Ensure both start_date and end_date are in the past"
    }
    
    # Symbol validation errors
    INVALID_SYMBOL = {
        "message": "Invalid or unsupported stock symbol",
        "suggestion": "Use valid stock symbols like AAPL, GOOGL, MSFT, TSLA",
        "supported_symbols": "Demo mode supports S&P 500 stocks. See full list at /api/v1/symbols"
    }
    
    NO_DATA_FOUND = {
        "message": "No market data available for this symbol and date range",
        "suggestions": [
            "Verify the stock symbol is correct",
            "Check if the company was publicly traded during this period",
            "Try a more recent date range",
            "Use a different symbol"
        ]
    }
    
    # Strategy errors
    STRATEGY_NOT_FOUND = {
        "message": "Strategy not found",
        "suggestion": "Use /api/v1/backtesting/demo/strategies to see available strategies",
        "common_strategies": [
            "ma_crossover",
            "rsi_strategy",
            "bollinger_bands",
            "momentum"
        ]
    }
    
    PREMIUM_STRATEGY = {
        "message": "This strategy requires a premium subscription",
        "demo_strategies": [
            "ma_crossover - Moving Average Crossover",
            "rsi_strategy - RSI Oscillator",
            "momentum - Momentum Strategy"
        ],
        "upgrade_url": "/pricing"
    }
    
    INVALID_STRATEGY_PARAMS = {
        "message": "Invalid strategy parameters",
        "suggestion": "Check the strategy documentation for required parameters",
        "example": {
            "strategy": "ma_crossover",
            "strategy_params": {
                "fast_period": 20,
                "slow_period": 50
            }
        }
    }
    
    # Capital errors
    INVALID_CAPITAL = {
        "message": "Initial capital must be positive",
        "suggestion": "Provide a capital amount greater than $0",
        "minimum": 1,
        "recommended_minimum": 10000,
        "example": 100000
    }
    
    CAPITAL_TOO_LOW = {
        "message": "Initial capital is very low",
        "warning": "Results may not be realistic with capital under $1,000",
        "recommended_minimum": 10000
    }
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = {
        "message": "Rate limit exceeded",
        "limit": "10 requests per hour for demo users",
        "suggestion": "Wait before making more requests, or upgrade to premium for higher limits",
        "premium_limits": "1000 requests per hour"
    }
    
    # General errors
    BACKTEST_EXECUTION_FAILED = {
        "message": "Backtest execution failed",
        "common_causes": [
            "Insufficient market data",
            "Invalid strategy parameters",
            "Data quality issues"
        ],
        "suggestion": "Try with different parameters or contact support"
    }
    
    @staticmethod
    def format_error(error_dict: Dict, detail: str = None) -> Dict:
        """Format error message with consistent structure"""
        response = {
            "error": error_dict["message"],
            **{k: v for k, v in error_dict.items() if k != "message"}
        }
        
        if detail:
            response["detail"] = detail
        
        return response
    
    @staticmethod
    def get_symbol_suggestions(symbol: str) -> List[str]:
        """Get symbol suggestions based on input"""
        popular_symbols = [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
            "META", "NVDA", "JPM", "V", "WMT"
        ]
        
        # Simple fuzzy matching
        suggestions = []
        for s in popular_symbols:
            if symbol.upper() in s or s in symbol.upper():
                suggestions.append(s)
        
        return suggestions[:5] if suggestions else popular_symbols[:5]


# Common validation functions
def validate_date_range(start_date, end_date, max_days=None):
    """Validate date range and return helpful error if invalid"""
    from datetime import datetime
    
    now = datetime.now()
    
    # Check order
    if end_date <= start_date:
        return BacktestErrorMessages.format_error(
            BacktestErrorMessages.DATE_ORDER_ERROR
        )
    
    # Check future dates
    if start_date > now or end_date > now:
        return BacktestErrorMessages.format_error(
            BacktestErrorMessages.FUTURE_DATE_ERROR
        )
    
    # Check duration
    duration = (end_date - start_date).days
    if max_days and duration > max_days:
        if max_days == 365:
            return BacktestErrorMessages.format_error(
                BacktestErrorMessages.DEMO_DURATION_ERROR,
                detail=f"Requested {duration} days, maximum is {max_days} days"
            )
        else:
            return BacktestErrorMessages.format_error(
                BacktestErrorMessages.MAX_DURATION_ERROR,
                detail=f"Requested {duration} days, maximum is {max_days} days"
            )
    
    return None


def validate_capital(capital: float):
    """Validate initial capital"""
    if capital <= 0:
        return BacktestErrorMessages.format_error(
            BacktestErrorMessages.INVALID_CAPITAL
        )
    
    if capital < 1000:
        # Warning, not error
        return {
            "warning": BacktestErrorMessages.CAPITAL_TOO_LOW,
            "can_proceed": True
        }
    
    return None
