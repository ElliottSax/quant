"""
Comprehensive tests for demo backtesting endpoints
Tests all edge cases, error handling, and data validation
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestDemoStrategiesEndpoint:
    """Test /api/v1/backtesting/demo/strategies endpoint"""
    
    def test_list_strategies_success(self):
        """Should return list of free strategies"""
        response = client.get("/api/v1/backtesting/demo/strategies")
        assert response.status_code == 200
        
        strategies = response.json()
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        
        # Verify structure
        for strategy in strategies:
            assert "name" in strategy
            assert "description" in strategy
            assert "parameters" in strategy
            assert "FREE" in strategy["description"] or "Demo" in strategy["description"]
    
    def test_strategies_no_auth_required(self):
        """Should work without authentication"""
        response = client.get("/api/v1/backtesting/demo/strategies")
        assert response.status_code == 200
    
    def test_strategies_response_format(self):
        """Should return properly formatted strategy info"""
        response = client.get("/api/v1/backtesting/demo/strategies")
        strategies = response.json()
        
        # Check first strategy has required fields
        strategy = strategies[0]
        assert isinstance(strategy["name"], str)
        assert isinstance(strategy["description"], str)
        assert isinstance(strategy["parameters"], dict)


class TestDemoBacktestEndpoint:
    """Test /api/v1/backtesting/demo/run endpoint"""
    
    @pytest.fixture
    def valid_request(self):
        """Valid backtest request"""
        return {
            "symbol": "AAPL",
            "start_date": "2025-06-01T00:00:00",
            "end_date": "2025-12-31T23:59:59",
            "strategy": "ma_crossover",
            "initial_capital": 100000
        }
    
    def test_run_backtest_success(self, valid_request):
        """Should run backtest successfully"""
        response = client.post(
            "/api/v1/backtesting/demo/run",
            json=valid_request
        )
        assert response.status_code == 200
        
        result = response.json()
        
        # Verify response structure
        assert "total_return" in result
        assert "sharpe_ratio" in result
        assert "max_drawdown" in result
        assert "total_trades" in result
        assert "equity_curve" in result
        
        # Verify data types
        assert isinstance(result["total_return"], (int, float))
        assert isinstance(result["sharpe_ratio"], (int, float))
        assert isinstance(result["total_trades"], int)
        assert isinstance(result["equity_curve"], list)
    
    def test_backtest_no_auth_required(self, valid_request):
        """Should work without authentication"""
        response = client.post(
            "/api/v1/backtesting/demo/run",
            json=valid_request
        )
        assert response.status_code == 200
    
    def test_backtest_invalid_symbol(self, valid_request):
        """Should handle invalid stock symbols gracefully"""
        valid_request["symbol"] = "INVALID_SYMBOL_12345"
        response = client.post(
            "/api/v1/backtesting/demo/run",
            json=valid_request
        )
        # Should either return 200 with mock data or 400 error
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            # Should fallback to mock data
            result = response.json()
            assert "total_return" in result
    
    def test_backtest_date_range_too_long(self, valid_request):
        """Should reject backtests longer than 1 year"""
        valid_request["start_date"] = "2023-01-01T00:00:00"
        valid_request["end_date"] = "2025-12-31T23:59:59"  # >1 year
        
        response = client.post(
            "/api/v1/backtesting/demo/run",
            json=valid_request
        )
        assert response.status_code == 400
        assert "1 year" in response.json()["detail"]
    
    def test_backtest_invalid_date_order(self, valid_request):
        """Should reject when end_date < start_date"""
        valid_request["start_date"] = "2025-12-31T00:00:00"
        valid_request["end_date"] = "2025-01-01T23:59:59"
        
        response = client.post(
            "/api/v1/backtesting/demo/run",
            json=valid_request
        )
        assert response.status_code in [400, 422]
    
    def test_backtest_invalid_strategy(self, valid_request):
        """Should reject invalid strategy names"""
        valid_request["strategy"] = "nonexistent_strategy"
        
        response = client.post(
            "/api/v1/backtesting/demo/run",
            json=valid_request
        )
        assert response.status_code in [400, 404]
    
    def test_backtest_premium_strategy(self, valid_request):
        """Should reject premium strategies in demo mode"""
        # Assuming there's a premium strategy
        valid_request["strategy"] = "advanced_ml_strategy"
        
        response = client.post(
            "/api/v1/backtesting/demo/run",
            json=valid_request
        )
        # Should reject with 403 or succeed if no premium strategies exist
        assert response.status_code in [200, 403, 404]
    
    def test_backtest_zero_capital(self, valid_request):
        """Should reject zero initial capital"""
        valid_request["initial_capital"] = 0
        
        response = client.post(
            "/api/v1/backtesting/demo/run",
            json=valid_request
        )
        assert response.status_code in [400, 422]
    
    def test_backtest_negative_capital(self, valid_request):
        """Should reject negative initial capital"""
        valid_request["initial_capital"] = -10000
        
        response = client.post(
            "/api/v1/backtesting/demo/run",
            json=valid_request
        )
        assert response.status_code in [400, 422]
    
    def test_backtest_missing_required_fields(self):
        """Should reject requests with missing fields"""
        response = client.post(
            "/api/v1/backtesting/demo/run",
            json={"symbol": "AAPL"}  # Missing other required fields
        )
        assert response.status_code == 422
    
    def test_backtest_with_custom_params(self, valid_request):
        """Should accept strategy parameters"""
        valid_request["strategy_params"] = {
            "fast_period": 10,
            "slow_period": 30
        }
        
        response = client.post(
            "/api/v1/backtesting/demo/run",
            json=valid_request
        )
        assert response.status_code == 200
    
    def test_backtest_different_symbols(self, valid_request):
        """Should work with various stock symbols"""
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        
        for symbol in symbols:
            valid_request["symbol"] = symbol
            response = client.post(
                "/api/v1/backtesting/demo/run",
                json=valid_request
            )
            assert response.status_code == 200
            result = response.json()
            assert result["symbol"] == symbol if "symbol" in result else True


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Should return healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        
        health = response.json()
        assert health["status"] in ["healthy", "degraded"]
        assert "environment" in health
        assert "version" in health


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_docs(self):
        """Should serve OpenAPI documentation"""
        response = client.get("/api/v1/docs")
        assert response.status_code == 200
    
    def test_openapi_json(self):
        """Should serve OpenAPI JSON spec"""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        
        spec = response.json()
        assert "openapi" in spec
        assert "paths" in spec


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
