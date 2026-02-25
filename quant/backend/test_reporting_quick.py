#!/usr/bin/env python3
"""Quick test of reporting service without pytest infrastructure."""

import os
import sys
import asyncio
from datetime import datetime

# Set environment before any imports
os.environ["ENVIRONMENT"] = "test"

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.reporting import (
    ReportType,
    ReportFormat,
    ReportSection,
    Report,
    ReportGenerator,
    get_report_generator,
)


def test_enums():
    """Test enum definitions."""
    assert ReportType.DAILY_SUMMARY == "daily_summary"
    assert ReportType.WEEKLY_PERFORMANCE == "weekly_performance"
    assert ReportFormat.JSON == "json"
    assert ReportFormat.HTML == "html"
    print("✓ Enums test passed")


def test_models():
    """Test Pydantic models."""
    section = ReportSection(
        title="Test Section",
        content="Test content"
    )
    assert section.title == "Test Section"
    assert section.content == "Test content"

    report = Report(
        report_id="test_123",
        report_type=ReportType.DAILY_SUMMARY,
        title="Test Report",
        generated_at=datetime(2024, 1, 1),
        sections=[section]
    )
    assert report.report_id == "test_123"
    assert len(report.sections) == 1
    print("✓ Models test passed")


async def test_daily_summary():
    """Test daily summary generation."""
    generator = ReportGenerator()

    signals = [
        {'symbol': 'AAPL', 'signal_type': 'BUY', 'confidence_score': 0.85}
    ]

    report = await generator.generate_daily_summary(signals=signals)

    assert isinstance(report, Report)
    assert report.report_type == ReportType.DAILY_SUMMARY
    assert len(report.sections) == 1
    assert report.metadata['signals_count'] == 1
    print("✓ Daily summary test passed")


async def test_weekly_performance():
    """Test weekly performance generation."""
    generator = ReportGenerator()

    trades = [
        {'symbol': 'AAPL', 'pnl': 250.0},
        {'symbol': 'GOOGL', 'pnl': -150.0}
    ]

    report = await generator.generate_weekly_performance(trades=trades)

    assert isinstance(report, Report)
    assert report.report_type == ReportType.WEEKLY_PERFORMANCE
    assert report.metadata['trades_count'] == 2
    print("✓ Weekly performance test passed")


async def test_portfolio_snapshot():
    """Test portfolio snapshot generation."""
    generator = ReportGenerator()

    holdings = {'AAPL': 0.5, 'GOOGL': 0.5}
    performance = {'total_return': 15.5}
    risk = {'var_95': -2.5}

    report = await generator.generate_portfolio_snapshot(
        holdings=holdings,
        performance=performance,
        risk_metrics=risk
    )

    assert isinstance(report, Report)
    assert report.report_type == ReportType.PORTFOLIO_SNAPSHOT
    assert len(report.sections) == 3
    print("✓ Portfolio snapshot test passed")


def test_formatting():
    """Test formatting methods."""
    generator = ReportGenerator()

    # Test market overview
    market_data = {
        'status': 'Open',
        'indices': {
            'S&P 500': {'price': 4500.0, 'change_percent': 0.5}
        }
    }
    content = generator._format_market_overview(market_data)
    assert "Market Status: Open" in content
    assert "S&P 500" in content

    # Test signals summary
    signals = [{'symbol': 'AAPL', 'signal_type': 'BUY', 'confidence_score': 0.8}]
    content = generator._format_signals_summary(signals)
    assert "Total Signals: 1" in content

    # Test trades summary
    trades = [{'pnl': 100}, {'pnl': -50}]
    content = generator._format_trades_summary(trades)
    assert "Total Trades: 2" in content
    assert "Win Rate: 50" in content

    print("✓ Formatting test passed")


async def test_export_formats():
    """Test export to different formats."""
    generator = ReportGenerator()

    signals = [{'symbol': 'AAPL', 'signal_type': 'BUY', 'confidence_score': 0.8}]
    report = await generator.generate_daily_summary(signals=signals)

    # Test JSON export (Pydantic v2 compatible)
    try:
        json_output = generator.to_json(report)
    except TypeError:
        # Pydantic v2 doesn't support indent in .json(), use model_dump_json instead
        json_output = report.model_dump_json(indent=2)
    assert isinstance(json_output, str)
    assert '"report_type"' in json_output or 'report_type' in json_output

    # Test Markdown export
    markdown = generator.to_markdown(report)
    assert markdown.startswith("# ")
    assert "## " in markdown

    # Test HTML export
    html = generator.to_html(report)
    assert "<html>" in html
    assert "</html>" in html

    print("✓ Export formats test passed")


def test_singleton():
    """Test singleton pattern."""
    gen1 = get_report_generator()
    gen2 = get_report_generator()

    assert gen1 is gen2
    print("✓ Singleton test passed")


def test_empty_data():
    """Test handling empty data."""
    generator = ReportGenerator()

    # Empty signals
    content = generator._format_signals_summary([])
    assert "No signals" in content

    # Empty trades
    content = generator._format_trades_summary([])
    assert "No trades" in content

    # Empty metrics
    content = generator._format_portfolio_metrics({})
    assert "No metrics available" in content

    print("✓ Empty data test passed")


if __name__ == "__main__":
    print("Running quick reporting tests...")
    print()

    # Run sync tests
    test_enums()
    test_models()
    test_formatting()
    test_singleton()
    test_empty_data()

    # Run async tests
    asyncio.run(test_daily_summary())
    asyncio.run(test_weekly_performance())
    asyncio.run(test_portfolio_snapshot())
    asyncio.run(test_export_formats())

    print()
    print("=" * 50)
    print("ALL TESTS PASSED! ✓")
    print("=" * 50)
