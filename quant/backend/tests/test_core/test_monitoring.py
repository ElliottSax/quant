"""
Tests for monitoring module.

Tests Sentry configuration and sensitive data filtering.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock

from app.core.monitoring import (
    setup_sentry,
    filter_sensitive_data,
    capture_exception,
    capture_message,
    set_user_context,
)


class TestSetupSentry:
    """Test Sentry initialization."""

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_setup_sentry_with_dsn(self, mock_sentry, mock_settings):
        """Test that Sentry initializes when DSN is configured."""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"
        mock_settings.SENTRY_ENVIRONMENT = "production"
        mock_settings.ENVIRONMENT = "production"
        mock_settings.VERSION = "1.0.0"

        setup_sentry()

        # Should call sentry_sdk.init
        mock_sentry.init.assert_called_once()

        # Check initialization arguments
        call_args = mock_sentry.init.call_args[1]
        assert call_args["dsn"] == "https://example@sentry.io/123"
        assert call_args["environment"] == "production"
        assert call_args["release"] == "quant@1.0.0"

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_setup_sentry_without_dsn(self, mock_sentry, mock_settings):
        """Test that Sentry does not initialize without DSN."""
        mock_settings.SENTRY_DSN = ""

        setup_sentry()

        # Should not call sentry_sdk.init
        mock_sentry.init.assert_not_called()

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_setup_sentry_development_sampling(self, mock_sentry, mock_settings):
        """Test that development uses higher sampling rates."""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"
        mock_settings.SENTRY_ENVIRONMENT = "development"
        mock_settings.ENVIRONMENT = "development"
        mock_settings.VERSION = "1.0.0"

        setup_sentry()

        call_args = mock_sentry.init.call_args[1]
        assert call_args["traces_sample_rate"] == 1.0
        assert call_args["profiles_sample_rate"] == 1.0

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_setup_sentry_production_sampling(self, mock_sentry, mock_settings):
        """Test that production uses lower sampling rates."""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"
        mock_settings.SENTRY_ENVIRONMENT = "production"
        mock_settings.ENVIRONMENT = "production"
        mock_settings.VERSION = "1.0.0"

        setup_sentry()

        call_args = mock_sentry.init.call_args[1]
        assert call_args["traces_sample_rate"] == 0.1
        assert call_args["profiles_sample_rate"] == 0.1

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_setup_sentry_handles_exception(self, mock_sentry, mock_settings):
        """Test that setup_sentry handles initialization errors gracefully."""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"
        mock_settings.SENTRY_ENVIRONMENT = "production"
        mock_settings.ENVIRONMENT = "production"
        mock_settings.VERSION = "1.0.0"

        mock_sentry.init.side_effect = Exception("Sentry init failed")

        # Should not raise exception
        setup_sentry()


class TestFilterSensitiveData:
    """Test sensitive data filtering for Sentry events."""

    def test_filter_authorization_header(self):
        """Test that Authorization header is filtered."""
        event = {
            "request": {
                "headers": {
                    "Authorization": "Bearer secret_token_12345",
                    "Content-Type": "application/json"
                }
            }
        }

        filtered = filter_sensitive_data(event, {})

        assert filtered["request"]["headers"]["Authorization"] == "[Filtered]"
        assert filtered["request"]["headers"]["Content-Type"] == "application/json"

    def test_filter_authorization_header_lowercase(self):
        """Test that lowercase authorization header is filtered."""
        event = {
            "request": {
                "headers": {
                    "authorization": "Bearer secret_token",
                }
            }
        }

        filtered = filter_sensitive_data(event, {})

        assert filtered["request"]["headers"]["authorization"] == "[Filtered]"

    def test_filter_cookie_header(self):
        """Test that Cookie header is filtered."""
        event = {
            "request": {
                "headers": {
                    "Cookie": "session=abc123; csrf=xyz789"
                }
            }
        }

        filtered = filter_sensitive_data(event, {})

        assert filtered["request"]["headers"]["Cookie"] == "[Filtered]"

    def test_filter_sensitive_query_parameters(self):
        """Test that sensitive query parameters are filtered."""
        test_cases = [
            "password=secret123&user=john",
            "token=abc123&action=login",
            "api_key=xyz789&format=json",
            "secret=hidden&data=test"
        ]

        for query_string in test_cases:
            event = {
                "request": {
                    "query_string": query_string
                }
            }

            filtered = filter_sensitive_data(event, {})

            assert filtered["request"]["query_string"] == "[Filtered]"

    def test_does_not_filter_safe_query_parameters(self):
        """Test that safe query parameters are not filtered."""
        event = {
            "request": {
                "query_string": "ticker=AAPL&limit=10&offset=0"
            }
        }

        filtered = filter_sensitive_data(event, {})

        # Should not be filtered
        assert "AAPL" in filtered["request"]["query_string"]

    def test_filter_sensitive_extra_context(self):
        """Test that sensitive keys in extra context are filtered."""
        event = {
            "extra": {
                "user_password": "secret123",
                "api_key": "xyz789",
                "user_email": "user@example.com",
                "safe_data": "this is fine"
            }
        }

        filtered = filter_sensitive_data(event, {})

        assert filtered["extra"]["user_password"] == "[Filtered]"
        assert filtered["extra"]["api_key"] == "[Filtered]"
        assert filtered["extra"]["safe_data"] == "this is fine"
        assert filtered["extra"]["user_email"] == "user@example.com"

    def test_filter_token_in_extra(self):
        """Test that tokens are filtered from extra context."""
        event = {
            "extra": {
                "access_token": "secret_access_token",
                "refresh_token": "secret_refresh_token",
                "regular_data": "not sensitive"
            }
        }

        filtered = filter_sensitive_data(event, {})

        assert filtered["extra"]["access_token"] == "[Filtered]"
        assert filtered["extra"]["refresh_token"] == "[Filtered]"
        assert filtered["extra"]["regular_data"] == "not sensitive"

    def test_filter_returns_event(self):
        """Test that filter_sensitive_data returns the event."""
        event = {
            "message": "Test event",
            "extra": {}
        }

        filtered = filter_sensitive_data(event, {})

        assert filtered is not None
        assert "message" in filtered

    def test_filter_with_no_request(self):
        """Test filtering works when event has no request."""
        event = {
            "message": "Test event without request"
        }

        filtered = filter_sensitive_data(event, {})

        assert filtered == event

    def test_filter_with_no_extra(self):
        """Test filtering works when event has no extra context."""
        event = {
            "request": {
                "headers": {
                    "Authorization": "Bearer token"
                }
            }
        }

        filtered = filter_sensitive_data(event, {})

        assert "extra" not in filtered


class TestCaptureException:
    """Test exception capturing."""

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_capture_exception_with_dsn(self, mock_sentry, mock_settings):
        """Test that exceptions are captured when Sentry is configured."""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"

        exception = ValueError("Test error")

        capture_exception(exception)

        mock_sentry.capture_exception.assert_called_once_with(exception)

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_capture_exception_without_dsn(self, mock_sentry, mock_settings):
        """Test that exceptions are not captured without DSN."""
        mock_settings.SENTRY_DSN = ""

        exception = ValueError("Test error")

        capture_exception(exception)

        mock_sentry.capture_exception.assert_not_called()

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_capture_exception_with_context(self, mock_sentry, mock_settings):
        """Test that extra context is attached to exceptions."""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"

        # Mock push_scope context manager
        mock_scope = MagicMock()
        mock_sentry.push_scope.return_value.__enter__.return_value = mock_scope

        exception = ValueError("Test error")

        capture_exception(exception, user_id="123", action="test")

        # Should set extra context
        assert mock_scope.set_extra.call_count == 2


class TestCaptureMessage:
    """Test message capturing."""

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_capture_message_with_dsn(self, mock_sentry, mock_settings):
        """Test that messages are captured when Sentry is configured."""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"

        capture_message("Test message", level="info")

        mock_sentry.capture_message.assert_called_once_with("Test message", level="info")

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_capture_message_without_dsn(self, mock_sentry, mock_settings):
        """Test that messages are not captured without DSN."""
        mock_settings.SENTRY_DSN = ""

        capture_message("Test message")

        mock_sentry.capture_message.assert_not_called()

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_capture_message_with_context(self, mock_sentry, mock_settings):
        """Test that extra context is attached to messages."""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"

        # Mock push_scope
        mock_scope = MagicMock()
        mock_sentry.push_scope.return_value.__enter__.return_value = mock_scope

        capture_message("Test message", level="warning", request_id="abc123")

        mock_scope.set_extra.assert_called_once_with("request_id", "abc123")

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_capture_message_different_levels(self, mock_sentry, mock_settings):
        """Test capturing messages with different severity levels."""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"

        levels = ["debug", "info", "warning", "error", "fatal"]

        for level in levels:
            capture_message(f"Test {level} message", level=level)

        # Should be called once for each level
        assert mock_sentry.capture_message.call_count == len(levels)


class TestSetUserContext:
    """Test setting user context."""

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_set_user_context_with_dsn(self, mock_sentry, mock_settings):
        """Test that user context is set when Sentry is configured."""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"

        set_user_context(user_id="123", email="user@example.com", username="testuser")

        mock_sentry.set_user.assert_called_once()

        call_args = mock_sentry.set_user.call_args[0][0]
        assert call_args["id"] == "123"
        assert call_args["email"] == "user@example.com"
        assert call_args["username"] == "testuser"

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_set_user_context_without_dsn(self, mock_sentry, mock_settings):
        """Test that user context is not set without DSN."""
        mock_settings.SENTRY_DSN = ""

        set_user_context(user_id="123")

        mock_sentry.set_user.assert_not_called()

    @patch("app.core.monitoring.settings")
    @patch("app.core.monitoring.sentry_sdk")
    def test_set_user_context_optional_fields(self, mock_sentry, mock_settings):
        """Test setting user context with optional fields."""
        mock_settings.SENTRY_DSN = "https://example@sentry.io/123"

        # Just user_id
        set_user_context(user_id="123")

        call_args = mock_sentry.set_user.call_args[0][0]
        assert call_args["id"] == "123"
        assert call_args.get("email") is None
        assert call_args.get("username") is None
