"""
Tests for signals API endpoints.

Tests WebSocket and REST endpoints for trading signal generation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.v1.signals import (
    SignalRequest,
    SignalResponse,
    WebSocketManager,
    router,
)


class TestSignalRequest:
    """Test SignalRequest model."""

    def test_init_with_required_fields(self):
        """Test creating request with required fields."""
        request = SignalRequest(
            symbol="AAPL",
            price_data=[100.0, 101.0, 102.0]
        )

        assert request.symbol == "AAPL"
        assert request.price_data == [100.0, 101.0, 102.0]
        assert request.volume_data is None
        assert request.use_ai is True

    def test_init_with_all_fields(self):
        """Test creating request with all fields."""
        request = SignalRequest(
            symbol="TSLA",
            price_data=[200.0, 205.0, 210.0],
            volume_data=[1000000, 1100000, 1200000],
            use_ai=False
        )

        assert request.symbol == "TSLA"
        assert request.price_data == [200.0, 205.0, 210.0]
        assert request.volume_data == [1000000, 1100000, 1200000]
        assert request.use_ai is False

    def test_default_use_ai(self):
        """Test that use_ai defaults to True."""
        request = SignalRequest(
            symbol="AAPL",
            price_data=[100.0]
        )

        assert request.use_ai is True


class TestSignalResponse:
    """Test SignalResponse model."""

    def test_init_with_fields(self):
        """Test creating response with fields."""
        mock_signal = Mock()
        generated_at = datetime(2024, 1, 1, 12, 0, 0)

        response = SignalResponse(
            signal=mock_signal,
            generated_at=generated_at
        )

        assert response.signal == mock_signal
        assert response.generated_at == generated_at


class TestWebSocketManager:
    """Test WebSocketManager functionality."""

    @pytest.mark.asyncio
    async def test_connect_new_symbol(self):
        """Test connecting to a new symbol."""
        manager = WebSocketManager()
        mock_websocket = AsyncMock()

        await manager.connect(mock_websocket, "AAPL")

        assert "AAPL" in manager.active_connections
        assert mock_websocket in manager.active_connections["AAPL"]
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_existing_symbol(self):
        """Test connecting another client to existing symbol."""
        manager = WebSocketManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()

        await manager.connect(mock_ws1, "AAPL")
        await manager.connect(mock_ws2, "AAPL")

        assert len(manager.active_connections["AAPL"]) == 2
        assert mock_ws1 in manager.active_connections["AAPL"]
        assert mock_ws2 in manager.active_connections["AAPL"]

    def test_disconnect_removes_websocket(self):
        """Test disconnecting removes websocket from connections."""
        manager = WebSocketManager()
        mock_websocket = Mock()

        # Manually add connection
        manager.active_connections["AAPL"] = [mock_websocket]

        manager.disconnect(mock_websocket, "AAPL")

        assert "AAPL" not in manager.active_connections

    def test_disconnect_removes_symbol_when_empty(self):
        """Test that symbol is removed when last connection disconnects."""
        manager = WebSocketManager()
        mock_ws1 = Mock()
        mock_ws2 = Mock()

        # Add two connections
        manager.active_connections["AAPL"] = [mock_ws1, mock_ws2]

        # Disconnect first
        manager.disconnect(mock_ws1, "AAPL")
        assert "AAPL" in manager.active_connections
        assert len(manager.active_connections["AAPL"]) == 1

        # Disconnect second
        manager.disconnect(mock_ws2, "AAPL")
        assert "AAPL" not in manager.active_connections

    def test_disconnect_nonexistent_symbol(self):
        """Test disconnecting from nonexistent symbol doesn't error."""
        manager = WebSocketManager()
        mock_websocket = Mock()

        # Should not raise exception
        manager.disconnect(mock_websocket, "NONEXISTENT")

    def test_disconnect_nonexistent_websocket(self):
        """Test disconnecting nonexistent websocket doesn't error."""
        manager = WebSocketManager()
        mock_ws1 = Mock()
        mock_ws2 = Mock()

        manager.active_connections["AAPL"] = [mock_ws1]

        # Should not raise exception
        manager.disconnect(mock_ws2, "AAPL")

        # Original connection should still be there
        assert mock_ws1 in manager.active_connections["AAPL"]

    @pytest.mark.asyncio
    async def test_broadcast_signal_to_all_connections(self):
        """Test broadcasting signal to all connected clients."""
        manager = WebSocketManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_signal = Mock()
        mock_signal.dict.return_value = {"type": "BUY", "price": 100}

        # Add connections
        manager.active_connections["AAPL"] = [mock_ws1, mock_ws2]

        await manager.broadcast_signal("AAPL", mock_signal)

        # Both connections should receive the signal
        mock_ws1.send_json.assert_called_once_with({"type": "BUY", "price": 100})
        mock_ws2.send_json.assert_called_once_with({"type": "BUY", "price": 100})

    @pytest.mark.asyncio
    async def test_broadcast_signal_handles_disconnected_clients(self):
        """Test that broadcast removes disconnected clients."""
        manager = WebSocketManager()
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_signal = Mock()
        mock_signal.dict.return_value = {}

        # Make ws1 fail to send
        mock_ws1.send_json.side_effect = Exception("Connection closed")

        manager.active_connections["AAPL"] = [mock_ws1, mock_ws2]

        await manager.broadcast_signal("AAPL", mock_signal)

        # ws1 should be removed, ws2 should still be there
        assert mock_ws1 not in manager.active_connections["AAPL"]
        assert mock_ws2 in manager.active_connections["AAPL"]

    @pytest.mark.asyncio
    async def test_broadcast_to_nonexistent_symbol(self):
        """Test broadcasting to nonexistent symbol doesn't error."""
        manager = WebSocketManager()
        mock_signal = Mock()

        # Should not raise exception
        await manager.broadcast_signal("NONEXISTENT", mock_signal)

    @pytest.mark.asyncio
    async def test_generate_and_broadcast_signals(self):
        """Test generating and broadcasting signals."""
        manager = WebSocketManager()
        mock_signal = Mock()

        # Mock the signal generator
        with patch.object(manager.signal_generator, 'generate_signal', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_signal

            # Mock broadcast
            with patch.object(manager, 'broadcast_signal', new_callable=AsyncMock) as mock_broadcast:
                await manager.generate_and_broadcast_signals(
                    symbol="AAPL",
                    price_data=[100.0, 101.0],
                    volume_data=[1000, 1100]
                )

                # Should generate signal
                mock_generate.assert_called_once_with(
                    symbol="AAPL",
                    price_data=[100.0, 101.0],
                    volume_data=[1000, 1100]
                )

                # Should broadcast signal
                mock_broadcast.assert_called_once_with("AAPL", mock_signal)

    @pytest.mark.asyncio
    async def test_generate_and_broadcast_handles_errors(self):
        """Test that generate_and_broadcast handles errors gracefully."""
        manager = WebSocketManager()

        # Mock signal generator to raise error
        with patch.object(manager.signal_generator, 'generate_signal', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = Exception("Generation failed")

            # Should not raise exception (error is caught and printed)
            await manager.generate_and_broadcast_signals(
                symbol="AAPL",
                price_data=[100.0]
            )


class TestGenerateSignalEndpoint:
    """Test POST /generate endpoint."""

    @pytest.mark.asyncio
    async def test_generate_signal_success(self):
        """Test successful signal generation."""
        from app.api.v1.signals import generate_signal

        # Mock request
        request = SignalRequest(
            symbol="AAPL",
            price_data=[100.0, 101.0, 102.0],
            use_ai=True
        )

        # Mock user
        mock_user = Mock()

        # Mock signal generator
        mock_signal = Mock()
        mock_generator = AsyncMock()
        mock_generator.generate_signal.return_value = mock_signal

        with patch("app.api.v1.signals.get_signal_generator", return_value=mock_generator):
            response = await generate_signal(request, mock_user)

            assert isinstance(response, SignalResponse)
            assert response.signal == mock_signal
            assert isinstance(response.generated_at, datetime)

    @pytest.mark.asyncio
    async def test_generate_signal_with_volume_data(self):
        """Test signal generation with volume data."""
        from app.api.v1.signals import generate_signal

        request = SignalRequest(
            symbol="TSLA",
            price_data=[200.0, 205.0],
            volume_data=[1000000, 1100000],
            use_ai=False
        )

        mock_user = Mock()
        mock_signal = Mock()
        mock_generator = AsyncMock()
        mock_generator.generate_signal.return_value = mock_signal

        with patch("app.api.v1.signals.get_signal_generator", return_value=mock_generator):
            response = await generate_signal(request, mock_user)

            # Verify volume_data was passed
            call_args = mock_generator.generate_signal.call_args[1]
            assert call_args["volume_data"] == [1000000, 1100000]
            assert call_args["use_ai"] is False

    @pytest.mark.asyncio
    async def test_generate_signal_error_handling(self):
        """Test error handling in signal generation."""
        from app.api.v1.signals import generate_signal

        request = SignalRequest(
            symbol="AAPL",
            price_data=[100.0]
        )

        mock_user = Mock()
        mock_generator = AsyncMock()
        mock_generator.generate_signal.side_effect = Exception("Generation failed")

        with patch("app.api.v1.signals.get_signal_generator", return_value=mock_generator):
            with pytest.raises(HTTPException) as exc_info:
                await generate_signal(request, mock_user)

            assert exc_info.value.status_code == 500
            assert "Error generating signal" in exc_info.value.detail


class TestGetLatestSignalEndpoint:
    """Test GET /latest/{symbol} endpoint."""

    @pytest.mark.asyncio
    async def test_get_latest_signal_not_implemented(self):
        """Test that get_latest_signal returns 404 (not implemented yet)."""
        from app.api.v1.signals import get_latest_signal

        mock_user = Mock()

        with pytest.raises(HTTPException) as exc_info:
            await get_latest_signal("AAPL", mock_user)

        assert exc_info.value.status_code == 404
        assert "No cached signal found" in exc_info.value.detail


class TestGetSignalHistoryEndpoint:
    """Test GET /history/{symbol} endpoint."""

    @pytest.mark.asyncio
    async def test_get_signal_history_returns_placeholder(self):
        """Test that signal history returns placeholder data."""
        from app.api.v1.signals import get_signal_history

        mock_user = Mock()

        response = await get_signal_history(
            symbol="AAPL",
            limit=100,
            current_user=mock_user
        )

        assert response["symbol"] == "AAPL"
        assert response["signals"] == []
        assert response["count"] == 0
        assert "coming soon" in response["message"].lower()

    @pytest.mark.asyncio
    async def test_get_signal_history_with_filters(self):
        """Test signal history with date filters."""
        from app.api.v1.signals import get_signal_history

        mock_user = Mock()
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)

        # Should not raise exception
        response = await get_signal_history(
            symbol="TSLA",
            limit=50,
            start_date=start_date,
            end_date=end_date,
            current_user=mock_user
        )

        assert response["symbol"] == "TSLA"


class TestGetSignalPerformanceEndpoint:
    """Test GET /performance/{symbol} endpoint."""

    @pytest.mark.asyncio
    async def test_get_signal_performance_returns_placeholder(self):
        """Test that performance endpoint returns placeholder data."""
        from app.api.v1.signals import get_signal_performance

        mock_user = Mock()

        response = await get_signal_performance(
            symbol="AAPL",
            days=30,
            current_user=mock_user
        )

        assert response["symbol"] == "AAPL"
        assert response["period_days"] == 30
        assert "metrics" in response
        assert response["metrics"]["total_signals"] == 0

    @pytest.mark.asyncio
    async def test_get_signal_performance_custom_days(self):
        """Test performance endpoint with custom day period."""
        from app.api.v1.signals import get_signal_performance

        mock_user = Mock()

        response = await get_signal_performance(
            symbol="TSLA",
            days=90,
            current_user=mock_user
        )

        assert response["period_days"] == 90


class TestWebSocketManagerMultipleSymbols:
    """Test WebSocketManager with multiple symbols."""

    @pytest.mark.asyncio
    async def test_multiple_symbols_independent(self):
        """Test that connections to different symbols are independent."""
        manager = WebSocketManager()
        ws_aapl = AsyncMock()
        ws_tsla = AsyncMock()

        await manager.connect(ws_aapl, "AAPL")
        await manager.connect(ws_tsla, "TSLA")

        assert "AAPL" in manager.active_connections
        assert "TSLA" in manager.active_connections
        assert len(manager.active_connections["AAPL"]) == 1
        assert len(manager.active_connections["TSLA"]) == 1

    @pytest.mark.asyncio
    async def test_broadcast_only_to_specific_symbol(self):
        """Test that broadcast only sends to specific symbol."""
        manager = WebSocketManager()
        ws_aapl = AsyncMock()
        ws_tsla = AsyncMock()
        mock_signal = Mock()
        mock_signal.dict.return_value = {}

        await manager.connect(ws_aapl, "AAPL")
        await manager.connect(ws_tsla, "TSLA")

        # Broadcast only to AAPL
        await manager.broadcast_signal("AAPL", mock_signal)

        # Only AAPL connection should receive
        ws_aapl.send_json.assert_called_once()
        ws_tsla.send_json.assert_not_called()

    def test_disconnect_one_symbol_doesnt_affect_others(self):
        """Test that disconnecting from one symbol doesn't affect others."""
        manager = WebSocketManager()
        ws_aapl = Mock()
        ws_tsla = Mock()

        manager.active_connections["AAPL"] = [ws_aapl]
        manager.active_connections["TSLA"] = [ws_tsla]

        manager.disconnect(ws_aapl, "AAPL")

        # AAPL should be removed
        assert "AAPL" not in manager.active_connections
        # TSLA should still exist
        assert "TSLA" in manager.active_connections
        assert ws_tsla in manager.active_connections["TSLA"]


class TestWebSocketManagerConcurrency:
    """Test WebSocketManager concurrent operations."""

    @pytest.mark.asyncio
    async def test_concurrent_connections(self):
        """Test multiple concurrent connections."""
        manager = WebSocketManager()
        websockets = [AsyncMock() for _ in range(5)]

        # Connect all concurrently
        await asyncio.gather(*[
            manager.connect(ws, "AAPL")
            for ws in websockets
        ])

        assert len(manager.active_connections["AAPL"]) == 5

    @pytest.mark.asyncio
    async def test_concurrent_broadcasts(self):
        """Test concurrent broadcasts to different symbols."""
        manager = WebSocketManager()
        symbols = ["AAPL", "TSLA", "MSFT", "GOOGL"]

        # Set up connections for each symbol
        for symbol in symbols:
            ws = AsyncMock()
            manager.active_connections[symbol] = [ws]

        # Create mock signals
        mock_signals = [Mock(dict=lambda: {}) for _ in symbols]

        # Broadcast concurrently
        await asyncio.gather(*[
            manager.broadcast_signal(symbol, signal)
            for symbol, signal in zip(symbols, mock_signals)
        ])

        # All symbols should still have connections
        for symbol in symbols:
            assert symbol in manager.active_connections
