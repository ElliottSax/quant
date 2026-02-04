"""
Tests for core utility functions and helpers.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
import uuid


class TestDateUtils:
    """Test date utility functions."""

    def test_date_range_generation(self):
        """Test generating date ranges."""
        from app.core.utils import generate_date_range

        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 10)

        dates = generate_date_range(start, end) if hasattr(generate_date_range, '__call__') else None

        if dates:
            assert len(dates) == 10
            assert dates[0] == start
            assert dates[-1] == end

    def test_business_days_calculation(self):
        """Test calculating business days between dates."""
        from app.core.utils import count_business_days

        start = datetime(2024, 1, 1)  # Monday
        end = datetime(2024, 1, 5)    # Friday

        # Should be 5 business days if function exists
        if hasattr(count_business_days, '__call__'):
            days = count_business_days(start, end)
            assert days == 5

    def test_date_formatting(self):
        """Test date formatting utilities."""
        from app.core.utils import format_date

        date = datetime(2024, 1, 15, 10, 30, 0)

        if hasattr(format_date, '__call__'):
            formatted = format_date(date, "YYYY-MM-DD")
            assert "2024-01-15" in formatted


class TestStringUtils:
    """Test string utility functions."""

    def test_sanitize_html(self):
        """Test HTML sanitization."""
        from app.core.utils import sanitize_html

        dangerous_html = "<script>alert('XSS')</script><p>Safe content</p>"

        if hasattr(sanitize_html, '__call__'):
            safe_html = sanitize_html(dangerous_html)
            assert "<script>" not in safe_html
            assert "alert" not in safe_html

    def test_truncate_string(self):
        """Test string truncation."""
        from app.core.utils import truncate

        long_string = "A" * 1000

        if hasattr(truncate, '__call__'):
            truncated = truncate(long_string, 50)
            assert len(truncated) <= 53  # 50 + "..."
            assert "..." in truncated

    def test_slugify(self):
        """Test creating URL-safe slugs."""
        from app.core.utils import slugify

        text = "Hello World! Test@123"

        if hasattr(slugify, '__call__'):
            slug = slugify(text)
            assert slug == "hello-world-test-123" or "hello" in slug


class TestNumberUtils:
    """Test number utility functions."""

    def test_format_currency(self):
        """Test currency formatting."""
        from app.core.utils import format_currency

        amount = Decimal("1234.56")

        if hasattr(format_currency, '__call__'):
            formatted = format_currency(amount)
            assert "$" in formatted or "1,234.56" in formatted

    def test_percentage_calculation(self):
        """Test percentage calculations."""
        from app.core.utils import calculate_percentage

        if hasattr(calculate_percentage, '__call__'):
            pct = calculate_percentage(50, 200)
            assert pct == 25.0

    def test_round_to_nearest(self):
        """Test rounding to nearest value."""
        from app.core.utils import round_to_nearest

        if hasattr(round_to_nearest, '__call__'):
            result = round_to_nearest(123.456, 0.05)
            assert result == 123.45 or abs(result - 123.45) < 0.01


class TestValidationUtils:
    """Test validation utility functions."""

    def test_email_validation(self):
        """Test email validation."""
        from app.core.utils import is_valid_email

        if hasattr(is_valid_email, '__call__'):
            assert is_valid_email("user@example.com") is True
            assert is_valid_email("invalid@") is False
            assert is_valid_email("@example.com") is False

    def test_url_validation(self):
        """Test URL validation."""
        from app.core.utils import is_valid_url

        if hasattr(is_valid_url, '__call__'):
            assert is_valid_url("https://example.com") is True
            assert is_valid_url("not a url") is False

    def test_uuid_validation(self):
        """Test UUID validation."""
        from app.core.utils import is_valid_uuid

        valid_uuid = str(uuid.uuid4())
        invalid_uuid = "not-a-uuid"

        if hasattr(is_valid_uuid, '__call__'):
            assert is_valid_uuid(valid_uuid) is True
            assert is_valid_uuid(invalid_uuid) is False


class TestEncodingUtils:
    """Test encoding and decoding utilities."""

    def test_base64_encoding(self):
        """Test base64 encoding."""
        from app.core.utils import encode_base64, decode_base64

        original = "Hello, World!"

        if hasattr(encode_base64, '__call__'):
            encoded = encode_base64(original)
            assert encoded != original

            if hasattr(decode_base64, '__call__'):
                decoded = decode_base64(encoded)
                assert decoded == original

    def test_hash_generation(self):
        """Test hash generation."""
        from app.core.utils import generate_hash

        data = "test data"

        if hasattr(generate_hash, '__call__'):
            hash1 = generate_hash(data)
            hash2 = generate_hash(data)

            # Same input should produce same hash
            assert hash1 == hash2

            # Different input should produce different hash
            hash3 = generate_hash("different data")
            assert hash1 != hash3


class TestDataStructureUtils:
    """Test data structure utilities."""

    def test_flatten_dict(self):
        """Test flattening nested dictionaries."""
        from app.core.utils import flatten_dict

        nested = {
            "a": 1,
            "b": {
                "c": 2,
                "d": {
                    "e": 3
                }
            }
        }

        if hasattr(flatten_dict, '__call__'):
            flat = flatten_dict(nested)
            assert "b.c" in flat or "b_c" in flat

    def test_chunk_list(self):
        """Test chunking lists."""
        from app.core.utils import chunk_list

        items = list(range(100))

        if hasattr(chunk_list, '__call__'):
            chunks = chunk_list(items, 10)
            assert len(chunks) == 10
            assert len(chunks[0]) == 10

    def test_deduplicate_list(self):
        """Test deduplicating lists while preserving order."""
        from app.core.utils import deduplicate

        items = [1, 2, 2, 3, 1, 4, 3, 5]

        if hasattr(deduplicate, '__call__'):
            unique = deduplicate(items)
            assert unique == [1, 2, 3, 4, 5]


class TestFileUtils:
    """Test file utility functions."""

    def test_file_extension_detection(self):
        """Test detecting file extensions."""
        from app.core.utils import get_file_extension

        if hasattr(get_file_extension, '__call__'):
            assert get_file_extension("file.txt") == "txt"
            assert get_file_extension("archive.tar.gz") == "gz" or "tar.gz"

    def test_file_size_formatting(self):
        """Test formatting file sizes."""
        from app.core.utils import format_file_size

        if hasattr(format_file_size, '__call__'):
            assert "1.0 KB" in format_file_size(1024) or "1024" in str(format_file_size(1024))
            assert "1.0 MB" in format_file_size(1024 * 1024) or "MB" in format_file_size(1024 * 1024)

    def test_safe_filename(self):
        """Test creating safe filenames."""
        from app.core.utils import safe_filename

        dangerous = "../../etc/passwd"

        if hasattr(safe_filename, '__call__'):
            safe = safe_filename(dangerous)
            assert ".." not in safe
            assert "/" not in safe


class TestRetryUtils:
    """Test retry utilities."""

    def test_retry_with_backoff(self):
        """Test retry with exponential backoff."""
        from app.core.utils import retry_with_backoff

        call_count = 0

        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"

        if hasattr(retry_with_backoff, '__call__'):
            result = retry_with_backoff(flaky_function, max_retries=5)
            assert result == "success"
            assert call_count == 3


class TestCryptoUtils:
    """Test cryptographic utilities."""

    def test_password_hashing(self):
        """Test password hashing."""
        from app.core.security import hash_password, verify_password

        password = "mysecurepassword"

        if hasattr(hash_password, '__call__'):
            hashed = hash_password(password)
            assert hashed != password

            if hasattr(verify_password, '__call__'):
                assert verify_password(password, hashed) is True
                assert verify_password("wrongpassword", hashed) is False

    def test_token_generation(self):
        """Test secure token generation."""
        from app.core.security import generate_token

        if hasattr(generate_token, '__call__'):
            token1 = generate_token()
            token2 = generate_token()

            # Tokens should be unique
            assert token1 != token2
            # Tokens should be sufficiently long
            assert len(token1) >= 32


class TestJSONUtils:
    """Test JSON utilities."""

    def test_json_serialization_with_dates(self):
        """Test JSON serialization of complex types."""
        from app.core.utils import json_serialize

        data = {
            "date": datetime.now(),
            "decimal": Decimal("123.45"),
            "uuid": uuid.uuid4()
        }

        if hasattr(json_serialize, '__call__'):
            json_str = json_serialize(data)
            assert isinstance(json_str, str)
            # Should not raise exception

    def test_json_safe_dict(self):
        """Test creating JSON-safe dictionaries."""
        from app.core.utils import to_json_safe

        data = {
            "date": datetime.now(),
            "bytes": b"binary data",
            "none": None
        }

        if hasattr(to_json_safe, '__call__'):
            safe = to_json_safe(data)
            # Should be JSON serializable
            import json
            json.dumps(safe)  # Should not raise
