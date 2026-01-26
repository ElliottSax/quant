"""
Tests for cache module.

Tests caching functionality, JSON encoding/decoding, and cache key generation.
"""

import json
import pytest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch

from app.core.cache import (
    CacheJSONEncoder,
    cache_json_decoder,
    CacheManager,
    cache_with_ttl,
)


class TestCacheJSONEncoder:
    """Test custom JSON encoder for cache serialization."""

    def test_encode_datetime(self):
        """Test encoding datetime objects."""
        encoder = CacheJSONEncoder()
        dt = datetime(2024, 1, 1, 12, 30, 45)
        result = encoder.default(dt)

        assert result["__type__"] == "datetime"
        assert result["value"] == "2024-01-01T12:30:45"

    def test_encode_date(self):
        """Test encoding date objects."""
        encoder = CacheJSONEncoder()
        d = date(2024, 1, 1)
        result = encoder.default(d)

        assert result["__type__"] == "date"
        assert result["value"] == "2024-01-01"

    def test_encode_decimal(self):
        """Test encoding Decimal objects."""
        encoder = CacheJSONEncoder()
        dec = Decimal("123.45")
        result = encoder.default(dec)

        assert result["__type__"] == "decimal"
        assert result["value"] == "123.45"

    def test_encode_object_with_dict(self):
        """Test encoding objects with __dict__ attribute."""
        encoder = CacheJSONEncoder()

        class TestObj:
            def __init__(self):
                self.name = "test"
                self.value = 42

        obj = TestObj()
        result = encoder.default(obj)

        assert result["__type__"] == "object"
        assert result["value"]["name"] == "test"
        assert result["value"]["value"] == 42

    def test_full_json_encoding(self):
        """Test full JSON encoding with custom encoder."""
        data = {
            "datetime": datetime(2024, 1, 1, 12, 0, 0),
            "date": date(2024, 1, 1),
            "decimal": Decimal("99.99"),
            "string": "test",
            "number": 42
        }

        json_str = json.dumps(data, cls=CacheJSONEncoder)
        assert json_str is not None
        assert "2024-01-01" in json_str


class TestCacheJSONDecoder:
    """Test custom JSON decoder for cache deserialization."""

    def test_decode_datetime(self):
        """Test decoding datetime objects."""
        obj = {"__type__": "datetime", "value": "2024-01-01T12:30:45"}
        result = cache_json_decoder(obj)

        assert isinstance(result, datetime)
        assert result == datetime(2024, 1, 1, 12, 30, 45)

    def test_decode_date(self):
        """Test decoding date objects."""
        obj = {"__type__": "date", "value": "2024-01-01"}
        result = cache_json_decoder(obj)

        assert isinstance(result, date)
        assert result == date(2024, 1, 1)

    def test_decode_decimal(self):
        """Test decoding Decimal objects."""
        obj = {"__type__": "decimal", "value": "123.45"}
        result = cache_json_decoder(obj)

        assert isinstance(result, Decimal)
        assert result == Decimal("123.45")

    def test_decode_object(self):
        """Test decoding generic objects."""
        obj = {"__type__": "object", "value": {"name": "test", "value": 42}}
        result = cache_json_decoder(obj)

        assert isinstance(result, dict)
        assert result["name"] == "test"
        assert result["value"] == 42

    def test_decode_regular_dict(self):
        """Test that regular dicts pass through unchanged."""
        obj = {"regular": "dict", "no_type": "field"}
        result = cache_json_decoder(obj)

        assert result == obj

    def test_roundtrip_encoding_decoding(self):
        """Test full roundtrip of encoding and decoding."""
        original_data = {
            "datetime": datetime(2024, 1, 1, 12, 0, 0),
            "date": date(2024, 1, 1),
            "decimal": Decimal("99.99"),
            "string": "test",
            "number": 42
        }

        # Encode
        json_str = json.dumps(original_data, cls=CacheJSONEncoder)

        # Decode
        decoded_data = json.loads(json_str, object_hook=cache_json_decoder)

        assert decoded_data["datetime"] == original_data["datetime"]
        assert decoded_data["date"] == original_data["date"]
        assert decoded_data["decimal"] == original_data["decimal"]
        assert decoded_data["string"] == original_data["string"]
        assert decoded_data["number"] == original_data["number"]


class TestCacheManager:
    """Test CacheManager functionality."""

    def test_init_enabled_in_production(self):
        """Test that cache is enabled in production environment."""
        with patch("app.core.cache.settings") as mock_settings:
            mock_settings.ENVIRONMENT = "production"

            manager = CacheManager()
            assert manager.enabled is True

    def test_init_enabled_in_development(self):
        """Test that cache is enabled in development environment."""
        with patch("app.core.cache.settings") as mock_settings:
            mock_settings.ENVIRONMENT = "development"

            manager = CacheManager()
            assert manager.enabled is True

    def test_init_disabled_in_test(self):
        """Test that cache is disabled in test environment."""
        with patch("app.core.cache.settings") as mock_settings:
            mock_settings.ENVIRONMENT = "test"

            manager = CacheManager()
            assert manager.enabled is False

    def test_make_key_consistent(self):
        """Test that _make_key generates consistent keys."""
        manager = CacheManager()

        key1 = manager._make_key("test", ticker="AAPL", days=30)
        key2 = manager._make_key("test", ticker="AAPL", days=30)

        assert key1 == key2

    def test_make_key_different_params(self):
        """Test that _make_key generates different keys for different params."""
        manager = CacheManager()

        key1 = manager._make_key("test", ticker="AAPL", days=30)
        key2 = manager._make_key("test", ticker="AAPL", days=60)

        assert key1 != key2

    def test_make_key_order_independent(self):
        """Test that _make_key generates same key regardless of param order."""
        manager = CacheManager()

        key1 = manager._make_key("test", ticker="AAPL", days=30, politician="John")
        key2 = manager._make_key("test", politician="John", ticker="AAPL", days=30)

        assert key1 == key2

    def test_make_key_with_prefix(self):
        """Test that _make_key includes prefix in key."""
        manager = CacheManager()

        key = manager._make_key("patterns", ticker="AAPL")

        assert key.startswith("patterns:")

    @pytest.mark.asyncio
    async def test_get_returns_none_when_disabled(self):
        """Test that get returns None when caching is disabled."""
        manager = CacheManager()
        manager.enabled = False

        result = await manager.get("test_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_returns_none_when_no_client(self):
        """Test that get returns None when Redis client is not connected."""
        manager = CacheManager()
        manager.enabled = True
        manager.redis_client = None

        result = await manager.get("test_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_hit(self):
        """Test successful cache hit."""
        manager = CacheManager()
        manager.enabled = True

        # Mock Redis client
        mock_client = AsyncMock()
        test_data = {"key": "value"}
        mock_client.get.return_value = json.dumps(test_data)
        manager.redis_client = mock_client

        result = await manager.get("test_key")

        assert result == test_data
        mock_client.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_cache_miss(self):
        """Test cache miss (key not found)."""
        manager = CacheManager()
        manager.enabled = True

        # Mock Redis client
        mock_client = AsyncMock()
        mock_client.get.return_value = None
        manager.redis_client = mock_client

        result = await manager.get("test_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_handles_exception(self):
        """Test that get handles Redis exceptions gracefully."""
        manager = CacheManager()
        manager.enabled = True

        # Mock Redis client that raises exception
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Redis error")
        manager.redis_client = mock_client

        result = await manager.get("test_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_returns_false_when_disabled(self):
        """Test that set returns False when caching is disabled."""
        manager = CacheManager()
        manager.enabled = False

        result = await manager.set("test_key", {"data": "value"})

        assert result is False

    @pytest.mark.asyncio
    async def test_set_success(self):
        """Test successful cache set."""
        manager = CacheManager()
        manager.enabled = True

        # Mock Redis client
        mock_client = AsyncMock()
        mock_client.setex.return_value = True
        manager.redis_client = mock_client

        result = await manager.set("test_key", {"data": "value"}, ttl=300)

        assert result is True
        mock_client.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_with_complex_data(self):
        """Test set with complex data including datetime and Decimal."""
        manager = CacheManager()
        manager.enabled = True

        # Mock Redis client
        mock_client = AsyncMock()
        mock_client.setex.return_value = True
        manager.redis_client = mock_client

        complex_data = {
            "datetime": datetime(2024, 1, 1, 12, 0, 0),
            "decimal": Decimal("99.99"),
            "string": "test"
        }

        result = await manager.set("test_key", complex_data, ttl=300)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_when_disabled(self):
        """Test that delete returns False when caching is disabled."""
        manager = CacheManager()
        manager.enabled = False

        result = await manager.delete("test_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_success(self):
        """Test successful cache delete."""
        manager = CacheManager()
        manager.enabled = True

        # Mock Redis client
        mock_client = AsyncMock()
        mock_client.delete.return_value = 1
        manager.redis_client = mock_client

        result = await manager.delete("test_key")

        assert result is True
        mock_client.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_clear_pattern(self):
        """Test clearing keys by pattern."""
        manager = CacheManager()
        manager.enabled = True

        # Mock Redis client
        mock_client = AsyncMock()
        mock_client.keys.return_value = [b"pattern:1", b"pattern:2"]
        mock_client.delete.return_value = 2
        manager.redis_client = mock_client

        result = await manager.clear_pattern("pattern:*")

        assert result == 2
        mock_client.keys.assert_called_once_with("pattern:*")


class TestCacheDecorator:
    """Test cache_with_ttl decorator."""

    @pytest.mark.asyncio
    async def test_decorator_caches_result(self):
        """Test that decorator caches function result."""
        call_count = 0

        @cache_with_ttl(ttl=300, prefix="test")
        async def expensive_function(param1: str, param2: int):
            nonlocal call_count
            call_count += 1
            return {"result": f"{param1}_{param2}"}

        # Mock cache manager
        with patch("app.core.cache.cache_manager") as mock_cache:
            mock_cache.get.return_value = None
            mock_cache.set.return_value = True

            # First call - should execute function
            result1 = await expensive_function("test", 42)

            assert call_count == 1
            assert result1 == {"result": "test_42"}
            mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_decorator_returns_cached_value(self):
        """Test that decorator returns cached value on subsequent calls."""
        cached_result = {"result": "cached_value"}

        @cache_with_ttl(ttl=300, prefix="test")
        async def expensive_function(param1: str):
            return {"result": "fresh_value"}

        # Mock cache manager with cached value
        with patch("app.core.cache.cache_manager") as mock_cache:
            mock_cache.get.return_value = cached_result

            result = await expensive_function("test")

            assert result == cached_result
            mock_cache.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_decorator_handles_cache_failure(self):
        """Test that decorator works even if caching fails."""
        @cache_with_ttl(ttl=300, prefix="test")
        async def test_function(param: str):
            return {"result": param}

        # Mock cache manager that raises exception
        with patch("app.core.cache.cache_manager") as mock_cache:
            mock_cache.get.side_effect = Exception("Cache error")

            # Should still execute function
            result = await test_function("test")

            assert result == {"result": "test"}
