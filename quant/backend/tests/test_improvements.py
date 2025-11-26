"""
Comprehensive test suite for all improvements.
Tests N+1 fixes, rate limiting, audit logging, and config validation.
"""

import pytest
import asyncio
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import redis.asyncio as redis

# Test environment setup
os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32chars"
os.environ["DATABASE_URL"] = "postgresql://test_user:test_pass@localhost:5432/test_db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"

from app.core.config_validator import ConfigValidator
from app.core.rate_limit_enhanced import EnhancedRateLimiter, RateLimitTier
from app.core.audit import AuditLogger, AuditEventType, AuditSeverity, AuditEventSchema


# ============================================================================
# Config Validation Tests
# ============================================================================

class TestConfigValidation:
    """Test configuration validation."""
    
    def test_valid_config(self):
        """Test with valid configuration."""
        validator = ConfigValidator("test")
        
        # Mock environment variables
        with patch.dict(os.environ, {
            "PROJECT_NAME": "Test Project",
            "VERSION": "1.0.0",
            "API_V1_STR": "/api/v1",
            "ENVIRONMENT": "test",
            "SECRET_KEY": "a-very-secure-secret-key-for-testing-32chars",
            "DATABASE_URL": "postgresql://user:pass@localhost/db",
            "ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            "REFRESH_TOKEN_EXPIRE_DAYS": "7"
        }):
            result = validator.validate_all()
            assert result is True
            assert len(validator.errors) == 0
    
    def test_missing_required(self):
        """Test with missing required fields."""
        validator = ConfigValidator("test")
        
        with patch.dict(os.environ, {}, clear=True):
            result = validator.validate_all()
            assert result is False
            assert len(validator.errors) > 0
            assert any("SECRET_KEY" in error for error in validator.errors)
            assert any("DATABASE_URL" in error for error in validator.errors)
    
    def test_insecure_secret(self):
        """Test detection of insecure secret key."""
        validator = ConfigValidator("test")
        
        with patch.dict(os.environ, {
            "SECRET_KEY": "changeme-this-is-not-secure-key",
            "DATABASE_URL": "postgresql://user:pass@localhost/db"
        }):
            validator._validate_security()
            assert len(validator.errors) > 0
            assert any("insecure pattern" in error for error in validator.errors)
    
    def test_production_validation(self):
        """Test production-specific validations."""
        validator = ConfigValidator("production")
        
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "DEBUG": "true",  # Should fail in production
            "SECRET_KEY": "secure-production-key-with-enough-entropy-123",
            "DATABASE_URL": "postgresql://user:quant_password@localhost/db"  # Default password
        }):
            validator._validate_production()
            validator._validate_database()
            
            assert len(validator.errors) > 0
            assert any("DEBUG must be False" in error for error in validator.errors)
            assert any("Default password" in error for error in validator.errors)


# ============================================================================
# Rate Limiting Tests
# ============================================================================

@pytest.mark.asyncio
class TestEnhancedRateLimiting:
    """Test enhanced rate limiting."""
    
    async def test_rate_limit_basic(self):
        """Test basic rate limiting."""
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.zcount.return_value = 5
        mock_redis.zadd.return_value = 1
        mock_redis.expire.return_value = True
        mock_redis.pipeline.return_value = mock_redis
        mock_redis.execute.return_value = [0, 5]
        
        limiter = EnhancedRateLimiter(
            redis_client=mock_redis,
            default_limit=10,
            window_seconds=60
        )
        
        # Mock request
        request = Mock()
        request.url.path = "/api/v1/test"
        request.client.host = "192.168.1.1"
        request.headers = {}
        request.state = Mock()
        request.state.user_id = "user123"
        
        is_allowed, metadata = await limiter.check_rate_limit(request)
        
        assert is_allowed is True
        assert metadata["remaining"] == 4  # 10 - 5 - 1
        assert metadata["limit"] == 60  # Basic tier default
    
    async def test_rate_limit_exceeded(self):
        """Test rate limit exceeded scenario."""
        mock_redis = AsyncMock()
        mock_redis.zcount.return_value = 60  # At limit
        mock_redis.pipeline.return_value = mock_redis
        mock_redis.execute.return_value = [0, 60]
        mock_redis.zrange.return_value = [(b"timestamp", 1234567890)]
        
        limiter = EnhancedRateLimiter(
            redis_client=mock_redis,
            default_limit=60,
            window_seconds=60
        )
        
        request = Mock()
        request.url.path = "/api/v1/test"
        request.client.host = "192.168.1.1"
        request.headers = {}
        request.state = Mock()
        request.state.user_id = "user123"
        
        is_allowed, metadata = await limiter.check_rate_limit(request)
        
        assert is_allowed is False
        assert metadata["remaining"] == 0
        assert "reset" in metadata
    
    async def test_endpoint_specific_limits(self):
        """Test endpoint-specific rate limits."""
        mock_redis = AsyncMock()
        mock_redis.zcount.return_value = 2
        mock_redis.zadd.return_value = 1
        mock_redis.expire.return_value = True
        mock_redis.pipeline.return_value = mock_redis
        mock_redis.execute.return_value = [0, 2]
        
        limiter = EnhancedRateLimiter(
            redis_client=mock_redis,
            default_limit=60
        )
        
        # Test ML endpoint with lower limit
        request = Mock()
        request.url.path = "/api/v1/analytics/ensemble"
        request.client.host = "192.168.1.1"
        request.headers = {}
        request.state = Mock()
        request.state.user_id = "user123"
        
        is_allowed, metadata = await limiter.check_rate_limit(request)
        
        assert is_allowed is True
        # Ensemble endpoint has limit of 10, doubled for basic tier = 20
        assert metadata["limit"] == 20
    
    def test_tier_limits(self):
        """Test different tier limits."""
        assert RateLimitTier.LIMITS[RateLimitTier.FREE] == 20
        assert RateLimitTier.LIMITS[RateLimitTier.BASIC] == 60
        assert RateLimitTier.LIMITS[RateLimitTier.PREMIUM] == 200
        assert RateLimitTier.LIMITS[RateLimitTier.UNLIMITED] == float('inf')


# ============================================================================
# Audit Logging Tests
# ============================================================================

@pytest.mark.asyncio
class TestAuditLogging:
    """Test audit logging system."""
    
    async def test_log_event(self):
        """Test basic audit event logging."""
        mock_db = AsyncMock()
        audit_logger = AuditLogger(db_session=mock_db)
        
        event = AuditEventSchema(
            event_type=AuditEventType.LOGIN_SUCCESS,
            severity=AuditSeverity.INFO,
            user_id="user123",
            username="testuser",
            action="user_login",
            result="success"
        )
        
        # Mock request
        request = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {"User-Agent": "Test Browser"}
        request.method = "POST"
        request.url.path = "/api/v1/auth/login"
        
        with patch('app.core.audit.logger') as mock_logger:
            result = await audit_logger.log_event(event, request)
            
            # Verify logging was called
            mock_logger.info.assert_called()
            
            # Verify database operations
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
    
    async def test_log_login(self):
        """Test login audit logging."""
        audit_logger = AuditLogger()
        
        with patch('app.core.audit.logger') as mock_logger:
            # Test successful login
            await audit_logger.log_login(
                user_id="user123",
                username="testuser",
                success=True
            )
            
            mock_logger.info.assert_called()
            
            # Test failed login
            await audit_logger.log_login(
                user_id=None,
                username="baduser",
                success=False,
                error_message="Invalid credentials"
            )
            
            assert mock_logger.warning.call_count > 0
    
    async def test_log_data_access(self):
        """Test data access audit logging."""
        audit_logger = AuditLogger()
        
        with patch('app.core.audit.logger') as mock_logger:
            await audit_logger.log_data_access(
                user_id="user123",
                resource_type="politician",
                resource_id="pol456",
                action="view_trades",
                data_classification="internal"
            )
            
            mock_logger.info.assert_called()
    
    async def test_log_security_event(self):
        """Test security event logging."""
        audit_logger = AuditLogger()
        
        with patch('app.core.audit.logger') as mock_logger:
            await audit_logger.log_security_event(
                event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
                severity=AuditSeverity.WARNING,
                description="Rate limit exceeded for user",
                user_id="user123",
                metadata={"endpoint": "/api/v1/analytics", "limit": 10}
            )
            
            mock_logger.warning.assert_called()
    
    def test_extract_request_info(self):
        """Test request information extraction."""
        audit_logger = AuditLogger()
        
        # Test with normal IP
        request = Mock()
        request.client = Mock()
        request.client.host = "192.168.1.100"
        request.headers = {
            "User-Agent": "Mozilla/5.0",
            "X-Request-ID": "req123"
        }
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/api/v1/test"
        
        info = audit_logger._extract_request_info(request)
        
        assert info["ip_address"] == "192.168.*.*"  # Privacy protection
        assert info["user_agent"] == "Mozilla/5.0"
        assert info["request_method"] == "GET"
        assert info["request_path"] == "/api/v1/test"
        
        # Test with X-Forwarded-For header
        request.headers["X-Forwarded-For"] = "10.0.0.1, 192.168.1.1"
        info = audit_logger._extract_request_info(request)
        assert info["ip_address"] == "10.0.*.*"


# ============================================================================
# Optimized Query Tests
# ============================================================================

@pytest.mark.asyncio
class TestOptimizedQueries:
    """Test optimized database queries."""
    
    async def test_batch_loading(self):
        """Test batch loading of politicians with trades."""
        from app.api.v1.analytics_optimized import load_politicians_with_trades_batch
        
        # Mock database session
        mock_db = AsyncMock()
        mock_result = Mock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [
            Mock(
                id="pol1",
                trades=[
                    Mock(trade_date=datetime.now(timezone.utc)),
                    Mock(trade_date=datetime.now(timezone.utc) - timedelta(days=30))
                ]
            ),
            Mock(
                id="pol2",
                trades=[
                    Mock(trade_date=datetime.now(timezone.utc) - timedelta(days=60))
                ]
            )
        ]
        
        mock_db.execute.return_value = mock_result
        
        result = await load_politicians_with_trades_batch(
            mock_db,
            ["pol1", "pol2"],
            days_back=90
        )
        
        assert len(result) == 2
        assert "pol1" in result
        assert "pol2" in result
        
        # Verify only one query was executed (no N+1)
        mock_db.execute.assert_called_once()
    
    async def test_aggregated_summary(self):
        """Test aggregated summary query."""
        from app.api.v1.analytics_optimized import get_recent_activity_summary
        
        mock_db = AsyncMock()
        mock_result = Mock()
        mock_result.first.return_value = Mock(
            total_trades=150,
            active_politicians=45,
            unique_tickers=89,
            total_volume=25000000,
            avg_trade_size=166666
        )
        
        mock_db.execute.return_value = mock_result
        
        summary = await get_recent_activity_summary(mock_db, days=30)
        
        assert summary["total_trades"] == 150
        assert summary["active_politicians"] == 45
        assert summary["unique_tickers"] == 89
        assert summary["total_volume"] == 25000000
        
        # Verify single query
        mock_db.execute.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])