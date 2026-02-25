"""
Tests for custom exceptions and error handlers.

Tests exception classes and error handler functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException, Request, status
from sqlalchemy.exc import IntegrityError, DatabaseError
from pydantic import ValidationError, BaseModel, field_validator

from app.core.exceptions import (
    AppException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    BadRequestException,
    ConflictException,
    RateLimitException,
    app_exception_handler,
    http_exception_handler,
    database_error_handler,
    integrity_error_handler,
    validation_error_handler,
    general_exception_handler,
)


class TestAppException:
    """Test AppException base class."""

    def test_init_with_message(self):
        """Test creating exception with message."""
        exc = AppException("Test error")

        assert exc.message == "Test error"
        assert exc.status_code == 500
        assert exc.details == {}

    def test_init_with_status_code(self):
        """Test creating exception with custom status code."""
        exc = AppException("Test error", status_code=400)

        assert exc.status_code == 400

    def test_init_with_details(self):
        """Test creating exception with details."""
        details = {"field": "value", "count": 42}
        exc = AppException("Test error", details=details)

        assert exc.details == details

    def test_exception_inherits_from_exception(self):
        """Test that AppException inherits from Exception."""
        exc = AppException("Test")

        assert isinstance(exc, Exception)

    def test_str_representation(self):
        """Test string representation of exception."""
        exc = AppException("Test error message")

        assert str(exc) == "Test error message"


class TestNotFoundException:
    """Test NotFoundException."""

    def test_init_with_resource(self):
        """Test creating NotFoundException with resource."""
        exc = NotFoundException("User")

        assert exc.message == "User not found"
        assert exc.status_code == 404

    def test_init_with_identifier(self):
        """Test creating NotFoundException with identifier."""
        exc = NotFoundException("User", "123")

        assert exc.message == "User with identifier '123' not found"
        assert exc.status_code == 404

    def test_inherits_from_app_exception(self):
        """Test that NotFoundException inherits from AppException."""
        exc = NotFoundException("Test")

        assert isinstance(exc, AppException)


class TestUnauthorizedException:
    """Test UnauthorizedException."""

    def test_init_default_message(self):
        """Test creating exception with default message."""
        exc = UnauthorizedException()

        assert exc.message == "Unauthorized"
        assert exc.status_code == 401

    def test_init_custom_message(self):
        """Test creating exception with custom message."""
        exc = UnauthorizedException("Invalid token")

        assert exc.message == "Invalid token"
        assert exc.status_code == 401


class TestForbiddenException:
    """Test ForbiddenException."""

    def test_init_default_message(self):
        """Test creating exception with default message."""
        exc = ForbiddenException()

        assert exc.message == "Forbidden"
        assert exc.status_code == 403

    def test_init_custom_message(self):
        """Test creating exception with custom message."""
        exc = ForbiddenException("Insufficient permissions")

        assert exc.message == "Insufficient permissions"
        assert exc.status_code == 403


class TestBadRequestException:
    """Test BadRequestException."""

    def test_init_with_message(self):
        """Test creating exception with message."""
        exc = BadRequestException("Invalid input")

        assert exc.message == "Invalid input"
        assert exc.status_code == 400
        assert exc.details == {}

    def test_init_with_details(self):
        """Test creating exception with details."""
        details = {"field": "email", "error": "invalid format"}
        exc = BadRequestException("Invalid input", details=details)

        assert exc.details == details


class TestConflictException:
    """Test ConflictException."""

    def test_init_default_message(self):
        """Test creating exception with default message."""
        exc = ConflictException()

        assert exc.message == "Resource conflict"
        assert exc.status_code == 409

    def test_init_custom_message(self):
        """Test creating exception with custom message."""
        exc = ConflictException("Duplicate entry")

        assert exc.message == "Duplicate entry"


class TestRateLimitException:
    """Test RateLimitException."""

    def test_init_default_message(self):
        """Test creating exception with default message."""
        exc = RateLimitException()

        assert exc.message == "Rate limit exceeded"
        assert exc.status_code == 429

    def test_init_custom_message(self):
        """Test creating exception with custom message."""
        exc = RateLimitException("Too many requests")

        assert exc.message == "Too many requests"


class TestAppExceptionHandler:
    """Test app_exception_handler."""

    @pytest.mark.asyncio
    async def test_handler_returns_json_response(self):
        """Test that handler returns JSONResponse."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"

        exc = BadRequestException("Test error")

        with patch("app.core.exceptions.create_error_response") as mock_create_error:
            mock_error = Mock()
            mock_error.model_dump.return_value = {"error": "test"}
            mock_create_error.return_value = mock_error

            response = await app_exception_handler(request, exc)

            assert response.status_code == 400
            mock_create_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_handler_logs_error(self):
        """Test that handler logs the error."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "POST"

        exc = NotFoundException("User", "123")

        with patch("app.core.exceptions.logger") as mock_logger:
            with patch("app.core.exceptions.create_error_response") as mock_create_error:
                mock_error = Mock()
                mock_error.model_dump.return_value = {}
                mock_create_error.return_value = mock_error

                await app_exception_handler(request, exc)

                mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_handler_includes_details(self):
        """Test that handler includes exception details."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"

        details = {"field": "email"}
        exc = BadRequestException("Invalid", details=details)

        with patch("app.core.exceptions.create_error_response") as mock_create_error:
            mock_error = Mock()
            mock_error.model_dump.return_value = {}
            mock_create_error.return_value = mock_error

            await app_exception_handler(request, exc)

            call_args = mock_create_error.call_args[1]
            assert call_args["details"] == details


class TestHTTPExceptionHandler:
    """Test http_exception_handler."""

    @pytest.mark.asyncio
    async def test_handler_returns_json_response(self):
        """Test that handler returns JSONResponse."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"

        exc = HTTPException(status_code=404, detail="Not found")

        with patch("app.core.exceptions.create_error_response") as mock_create_error:
            mock_error = Mock()
            mock_error.model_dump.return_value = {}
            mock_create_error.return_value = mock_error

            response = await http_exception_handler(request, exc)

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_handler_logs_warning(self):
        """Test that handler logs a warning."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"

        exc = HTTPException(status_code=404, detail="Not found")

        with patch("app.core.exceptions.logger") as mock_logger:
            with patch("app.core.exceptions.create_error_response") as mock_create_error:
                mock_error = Mock()
                mock_error.model_dump.return_value = {}
                mock_create_error.return_value = mock_error

                await http_exception_handler(request, exc)

                mock_logger.warning.assert_called_once()


class TestDatabaseErrorHandler:
    """Test database_error_handler."""

    @pytest.mark.asyncio
    async def test_handler_returns_500(self):
        """Test that handler returns 500 status code."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "POST"

        exc = DatabaseError("Database connection failed", None, None)

        with patch("app.core.exceptions.create_error_response") as mock_create_error:
            mock_error = Mock()
            mock_error.model_dump.return_value = {}
            mock_create_error.return_value = mock_error

            response = await database_error_handler(request, exc)

            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_handler_hides_details(self):
        """Test that handler hides database error details."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "POST"

        exc = DatabaseError("SELECT * FROM users WHERE password='secret'", None, None)

        with patch("app.core.exceptions.create_error_response") as mock_create_error:
            mock_error = Mock()
            mock_error.model_dump.return_value = {}
            mock_create_error.return_value = mock_error

            await database_error_handler(request, exc)

            call_args = mock_create_error.call_args[1]
            # Should show generic message, not actual error
            assert "Database error occurred" in call_args["message"]


class TestIntegrityErrorHandler:
    """Test integrity_error_handler."""

    @pytest.mark.asyncio
    async def test_handler_returns_409(self):
        """Test that handler returns 409 status code."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "POST"

        exc = IntegrityError("Duplicate key", None, None)

        with patch("app.core.exceptions.create_error_response") as mock_create_error:
            mock_error = Mock()
            mock_error.model_dump.return_value = {}
            mock_create_error.return_value = mock_error

            response = await integrity_error_handler(request, exc)

            assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_handler_logs_warning(self):
        """Test that handler logs a warning."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "POST"

        exc = IntegrityError("Duplicate", None, None)

        with patch("app.core.exceptions.logger") as mock_logger:
            with patch("app.core.exceptions.create_error_response") as mock_create_error:
                mock_error = Mock()
                mock_error.model_dump.return_value = {}
                mock_create_error.return_value = mock_error

                await integrity_error_handler(request, exc)

                mock_logger.warning.assert_called_once()


class TestValidationErrorHandler:
    """Test validation_error_handler."""

    @pytest.mark.asyncio
    async def test_handler_returns_422(self):
        """Test that handler returns 422 status code."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "POST"

        # Create a simple validation error
        class TestModel(BaseModel):
            email: str

            @field_validator("email")
            @classmethod
            def validate_email(cls, v):
                if "@" not in v:
                    raise ValueError("Invalid email")
                return v

        try:
            TestModel(email="invalid")
        except ValidationError as exc:
            with patch("app.core.exceptions.create_error_response") as mock_create_error:
                mock_error = Mock()
                mock_error.model_dump.return_value = {}
                mock_create_error.return_value = mock_error

                response = await validation_error_handler(request, exc)

                assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_handler_converts_errors(self):
        """Test that handler converts Pydantic errors to ErrorDetail format."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "POST"

        class TestModel(BaseModel):
            email: str

            @field_validator("email")
            @classmethod
            def validate_email(cls, v):
                if "@" not in v:
                    raise ValueError("Invalid email")
                return v

        try:
            TestModel(email="invalid")
        except ValidationError as exc:
            with patch("app.core.exceptions.create_error_response") as mock_create_error:
                with patch("app.core.exceptions.ErrorDetail") as mock_error_detail:
                    mock_error = Mock()
                    mock_error.model_dump.return_value = {}
                    mock_create_error.return_value = mock_error

                    await validation_error_handler(request, exc)

                    # ErrorDetail should be called to create error objects
                    assert mock_error_detail.called


class TestGeneralExceptionHandler:
    """Test general_exception_handler."""

    @pytest.mark.asyncio
    async def test_handler_returns_500(self):
        """Test that handler returns 500 for unexpected errors."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"

        exc = Exception("Unexpected error")

        with patch("app.core.exceptions.create_error_response") as mock_create_error:
            mock_error = Mock()
            mock_error.model_dump.return_value = {}
            mock_create_error.return_value = mock_error

            response = await general_exception_handler(request, exc)

            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_handler_logs_error_with_traceback(self):
        """Test that handler logs error with traceback."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"

        exc = Exception("Unexpected error")

        with patch("app.core.exceptions.logger") as mock_logger:
            with patch("app.core.exceptions.create_error_response") as mock_create_error:
                mock_error = Mock()
                mock_error.model_dump.return_value = {}
                mock_create_error.return_value = mock_error

                await general_exception_handler(request, exc)

                # Should log with exc_info=True for traceback
                call_kwargs = mock_logger.error.call_args[1]
                assert call_kwargs.get("exc_info") is True

    @pytest.mark.asyncio
    async def test_handler_hides_error_details(self):
        """Test that handler doesn't expose internal error details."""
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"

        exc = Exception("Secret internal error with sensitive data")

        with patch("app.core.exceptions.create_error_response") as mock_create_error:
            mock_error = Mock()
            mock_error.model_dump.return_value = {}
            mock_create_error.return_value = mock_error

            await general_exception_handler(request, exc)

            call_args = mock_create_error.call_args[1]
            # Should show generic message
            assert "unexpected error occurred" in call_args["message"].lower()
