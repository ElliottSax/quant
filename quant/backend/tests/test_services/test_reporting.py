"""
Comprehensive tests for Reporting Service

Tests cover:
- Enums and models
- Report generation (daily, weekly, portfolio)
- Formatting methods
- Export formats (JSON, HTML, Markdown)
- Singleton pattern
- Empty data handling
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, List
import json

from app.services.reporting import (
    ReportType,
    ReportFormat,
    ReportSection,
    Report,
    ReportGenerator,
    get_report_generator,
)


# ==================== FIXTURES ====================

@pytest.fixture
def report_generator():
    """Create a report generator instance"""
    return ReportGenerator()


@pytest.fixture
def sample_signals():
    """Sample trading signals"""
    return [
        {
            'symbol': 'AAPL',
            'signal_type': 'BUY',
            'confidence_score': 0.85,
            'price': 150.0
        },
        {
            'symbol': 'GOOGL',
            'signal_type': 'SELL',
            'confidence_score': 0.75,
            'price': 2800.0
        },
        {
            'symbol': 'MSFT',
            'signal_type': 'HOLD',
            'confidence_score': 0.60,
            'price': 300.0
        }
    ]


@pytest.fixture
def sample_portfolio_metrics():
    """Sample portfolio metrics"""
    return {
        'total_return': 15.5,
        'sharpe_ratio': 1.8,
        'max_drawdown': -12.3,
        'volatility': 18.2
    }


@pytest.fixture
def sample_market_data():
    """Sample market data"""
    return {
        'status': 'Open',
        'indices': {
            'S&P 500': {'price': 4500.0, 'change_percent': 0.5},
            'NASDAQ': {'price': 15000.0, 'change_percent': -0.3},
            'DOW': {'price': 35000.0, 'change_percent': 0.2}
        }
    }


@pytest.fixture
def sample_trades():
    """Sample trades"""
    return [
        {'symbol': 'AAPL', 'pnl': 250.0, 'type': 'BUY'},
        {'symbol': 'GOOGL', 'pnl': -150.0, 'type': 'SELL'},
        {'symbol': 'MSFT', 'pnl': 500.0, 'type': 'BUY'},
        {'symbol': 'TSLA', 'pnl': 300.0, 'type': 'BUY'}
    ]


@pytest.fixture
def sample_returns():
    """Sample returns"""
    return {
        'weekly_return': 2.5,
        'mtd_return': 5.8,
        'ytd_return': 18.3
    }


@pytest.fixture
def sample_benchmarks():
    """Sample benchmarks"""
    return {
        'S&P 500': {'return': 1.5, 'alpha': 1.0, 'beta': 0.95},
        'NASDAQ': {'return': 2.0, 'alpha': 0.5, 'beta': 1.05}
    }


@pytest.fixture
def sample_holdings():
    """Sample portfolio holdings"""
    return {
        'AAPL': 0.30,
        'GOOGL': 0.25,
        'MSFT': 0.20,
        'TSLA': 0.15,
        'AMZN': 0.10
    }


@pytest.fixture
def sample_risk_metrics():
    """Sample risk metrics"""
    return {
        'var_95': -2.5,
        'cvar_95': -3.8,
        'beta': 1.05,
        'correlation': 0.85
    }


# ==================== ENUM TESTS ====================

class TestEnums:
    """Test enum definitions"""

    def test_report_type_values(self):
        """Test ReportType enum has expected types"""
        assert ReportType.DAILY_SUMMARY == "daily_summary"
        assert ReportType.WEEKLY_PERFORMANCE == "weekly_performance"
        assert ReportType.MONTHLY_ANALYSIS == "monthly_analysis"
        assert ReportType.PORTFOLIO_SNAPSHOT == "portfolio_snapshot"
        assert ReportType.SIGNAL_SUMMARY == "signal_summary"
        assert ReportType.CUSTOM == "custom"

    def test_report_type_count(self):
        """Test all report types are defined"""
        types = list(ReportType)
        assert len(types) == 6

    def test_report_format_values(self):
        """Test ReportFormat enum has expected formats"""
        assert ReportFormat.JSON == "json"
        assert ReportFormat.HTML == "html"
        assert ReportFormat.MARKDOWN == "markdown"
        assert ReportFormat.TEXT == "text"

    def test_report_format_count(self):
        """Test all report formats are defined"""
        formats = list(ReportFormat)
        assert len(formats) == 4


# ==================== MODEL TESTS ====================

class TestModels:
    """Test Pydantic models"""

    def test_report_section_creation(self):
        """Test creating a ReportSection"""
        section = ReportSection(
            title="Test Section",
            content="Test content",
            data={"key": "value"}
        )

        assert section.title == "Test Section"
        assert section.content == "Test content"
        assert section.data == {"key": "value"}

    def test_report_section_optional_data(self):
        """Test ReportSection with optional data"""
        section = ReportSection(
            title="Test",
            content="Content"
        )

        assert section.title == "Test"
        assert section.content == "Content"
        assert section.data is None

    def test_report_creation(self):
        """Test creating a Report"""
        sections = [
            ReportSection(title="Section 1", content="Content 1"),
            ReportSection(title="Section 2", content="Content 2")
        ]

        report = Report(
            report_id="test_123",
            report_type=ReportType.DAILY_SUMMARY,
            title="Test Report",
            generated_at=datetime(2024, 1, 1),
            sections=sections,
            metadata={"test": "data"}
        )

        assert report.report_id == "test_123"
        assert report.report_type == ReportType.DAILY_SUMMARY
        assert report.title == "Test Report"
        assert len(report.sections) == 2
        assert report.metadata == {"test": "data"}

    def test_report_default_metadata(self):
        """Test Report with default metadata"""
        report = Report(
            report_id="test",
            report_type=ReportType.CUSTOM,
            title="Test",
            generated_at=datetime(2024, 1, 1),
            sections=[]
        )

        assert report.metadata == {}


# ==================== DAILY SUMMARY TESTS ====================

class TestDailySummary:
    """Test daily summary report generation"""

    @pytest.mark.asyncio
    async def test_generate_daily_summary_full(
        self,
        report_generator,
        sample_signals,
        sample_portfolio_metrics,
        sample_market_data
    ):
        """Test generating complete daily summary"""
        report = await report_generator.generate_daily_summary(
            signals=sample_signals,
            portfolio_metrics=sample_portfolio_metrics,
            market_data=sample_market_data
        )

        assert isinstance(report, Report)
        assert report.report_type == ReportType.DAILY_SUMMARY
        assert len(report.sections) == 3  # Market, Signals, Portfolio
        assert report.metadata['signals_count'] == 3
        assert report.metadata['has_portfolio'] is True

    @pytest.mark.asyncio
    async def test_generate_daily_summary_signals_only(
        self,
        report_generator,
        sample_signals
    ):
        """Test daily summary with only signals"""
        report = await report_generator.generate_daily_summary(
            signals=sample_signals
        )

        assert len(report.sections) == 1
        assert report.sections[0].title == "Trading Signals"
        assert report.metadata['signals_count'] == 3

    @pytest.mark.asyncio
    async def test_generate_daily_summary_empty(self, report_generator):
        """Test daily summary with no data"""
        report = await report_generator.generate_daily_summary()

        assert isinstance(report, Report)
        assert len(report.sections) == 0
        assert report.metadata['signals_count'] == 0
        assert report.metadata['has_portfolio'] is False

    @pytest.mark.asyncio
    async def test_daily_summary_title_format(self, report_generator):
        """Test daily summary title includes date"""
        report = await report_generator.generate_daily_summary()

        assert "Daily Summary" in report.title
        assert report.report_id.startswith("daily_")


# ==================== WEEKLY PERFORMANCE TESTS ====================

class TestWeeklyPerformance:
    """Test weekly performance report generation"""

    @pytest.mark.asyncio
    async def test_generate_weekly_performance_full(
        self,
        report_generator,
        sample_trades,
        sample_returns,
        sample_benchmarks
    ):
        """Test generating complete weekly performance"""
        report = await report_generator.generate_weekly_performance(
            trades=sample_trades,
            returns=sample_returns,
            benchmarks=sample_benchmarks
        )

        assert isinstance(report, Report)
        assert report.report_type == ReportType.WEEKLY_PERFORMANCE
        assert len(report.sections) == 3  # Returns, Trades, Benchmarks
        assert report.metadata['trades_count'] == 4

    @pytest.mark.asyncio
    async def test_generate_weekly_performance_trades_only(
        self,
        report_generator,
        sample_trades
    ):
        """Test weekly performance with only trades"""
        report = await report_generator.generate_weekly_performance(
            trades=sample_trades
        )

        assert len(report.sections) == 1
        assert report.sections[0].title == "Trading Activity"

    @pytest.mark.asyncio
    async def test_generate_weekly_performance_empty(self, report_generator):
        """Test weekly performance with no data"""
        report = await report_generator.generate_weekly_performance()

        assert len(report.sections) == 0
        assert report.metadata['trades_count'] == 0

    @pytest.mark.asyncio
    async def test_weekly_performance_title_format(self, report_generator):
        """Test weekly performance title format"""
        report = await report_generator.generate_weekly_performance()

        assert "Weekly Performance" in report.title
        assert report.report_id.startswith("weekly_")


# ==================== PORTFOLIO SNAPSHOT TESTS ====================

class TestPortfolioSnapshot:
    """Test portfolio snapshot report generation"""

    @pytest.mark.asyncio
    async def test_generate_portfolio_snapshot(
        self,
        report_generator,
        sample_holdings,
        sample_portfolio_metrics,
        sample_risk_metrics
    ):
        """Test generating portfolio snapshot"""
        report = await report_generator.generate_portfolio_snapshot(
            holdings=sample_holdings,
            performance=sample_portfolio_metrics,
            risk_metrics=sample_risk_metrics
        )

        assert isinstance(report, Report)
        assert report.report_type == ReportType.PORTFOLIO_SNAPSHOT
        assert len(report.sections) == 3  # Holdings, Performance, Risk
        assert report.metadata['num_holdings'] == 5

    @pytest.mark.asyncio
    async def test_portfolio_snapshot_title_format(
        self,
        report_generator,
        sample_holdings,
        sample_portfolio_metrics,
        sample_risk_metrics
    ):
        """Test portfolio snapshot title format"""
        report = await report_generator.generate_portfolio_snapshot(
            holdings=sample_holdings,
            performance=sample_portfolio_metrics,
            risk_metrics=sample_risk_metrics
        )

        assert "Portfolio Snapshot" in report.title
        assert report.report_id.startswith("portfolio_")


# ==================== FORMATTING TESTS ====================

class TestFormatting:
    """Test formatting methods"""

    def test_format_market_overview(
        self,
        report_generator,
        sample_market_data
    ):
        """Test market overview formatting"""
        content = report_generator._format_market_overview(sample_market_data)

        assert "Market Status: Open" in content
        assert "S&P 500" in content
        assert "NASDAQ" in content
        assert "↑" in content or "↓" in content  # Arrow indicators

    def test_format_signals_summary(self, report_generator, sample_signals):
        """Test signals summary formatting"""
        content = report_generator._format_signals_summary(sample_signals)

        assert "Total Signals: 3" in content
        assert "BUY" in content
        assert "AAPL" in content
        assert "High Confidence Signals" in content

    def test_format_signals_summary_empty(self, report_generator):
        """Test signals summary with no signals"""
        content = report_generator._format_signals_summary([])

        assert "No signals generated today" in content

    def test_format_portfolio_metrics(
        self,
        report_generator,
        sample_portfolio_metrics
    ):
        """Test portfolio metrics formatting"""
        content = report_generator._format_portfolio_metrics(sample_portfolio_metrics)

        assert "Total Return" in content
        assert "15.5%" in content
        assert "Sharpe Ratio: 1.8" in content
        assert "Max Drawdown" in content

    def test_format_portfolio_metrics_empty(self, report_generator):
        """Test portfolio metrics with no data"""
        content = report_generator._format_portfolio_metrics({})

        assert "No metrics available" in content

    def test_format_returns_analysis(self, report_generator, sample_returns):
        """Test returns analysis formatting"""
        content = report_generator._format_returns_analysis(sample_returns)

        assert "Weekly Return" in content
        assert "2.5%" in content
        assert "Month-to-Date: 5.8%" in content
        assert "Year-to-Date: 18.3%" in content

    def test_format_trades_summary(self, report_generator, sample_trades):
        """Test trades summary formatting"""
        content = report_generator._format_trades_summary(sample_trades)

        assert "Total Trades: 4" in content
        assert "Winning: 3" in content
        assert "Losing: 1" in content
        assert "Win Rate: 75" in content

    def test_format_trades_summary_empty(self, report_generator):
        """Test trades summary with no trades"""
        content = report_generator._format_trades_summary([])

        assert "No trades this week" in content

    def test_format_benchmark_comparison(
        self,
        report_generator,
        sample_benchmarks
    ):
        """Test benchmark comparison formatting"""
        content = report_generator._format_benchmark_comparison(sample_benchmarks)

        assert "S&P 500" in content
        assert "NASDAQ" in content
        assert "Return:" in content
        assert "Alpha:" in content
        assert "Beta:" in content

    def test_format_benchmark_comparison_empty(self, report_generator):
        """Test benchmark comparison with no data"""
        content = report_generator._format_benchmark_comparison({})

        assert "No benchmark data" in content

    def test_format_holdings(self, report_generator, sample_holdings):
        """Test holdings formatting"""
        content = report_generator._format_holdings(sample_holdings)

        assert "Symbol | Weight" in content
        assert "AAPL" in content
        assert "30.0%" in content
        assert "GOOGL" in content

    def test_format_holdings_sorted(self, report_generator, sample_holdings):
        """Test holdings are sorted by weight"""
        content = report_generator._format_holdings(sample_holdings)

        lines = content.split('\n')
        # AAPL (30%) should come before AMZN (10%)
        aapl_index = next(i for i, line in enumerate(lines) if 'AAPL' in line)
        amzn_index = next(i for i, line in enumerate(lines) if 'AMZN' in line)
        assert aapl_index < amzn_index

    def test_format_risk_metrics(self, report_generator, sample_risk_metrics):
        """Test risk metrics formatting"""
        content = report_generator._format_risk_metrics(sample_risk_metrics)

        assert "VaR (95%)" in content
        assert "CVaR (95%)" in content
        assert "Market Beta: 1.05" in content
        assert "Market Correlation: 0.85" in content

    def test_format_risk_metrics_empty(self, report_generator):
        """Test risk metrics with no data"""
        content = report_generator._format_risk_metrics({})

        assert "No risk data" in content


# ==================== EXPORT TESTS ====================

class TestExport:
    """Test export to different formats"""

    @pytest.mark.asyncio
    async def test_to_json(
        self,
        report_generator,
        sample_signals
    ):
        """Test converting report to JSON"""
        report = await report_generator.generate_daily_summary(
            signals=sample_signals
        )

        json_output = report_generator.to_json(report)

        assert isinstance(json_output, str)
        # Verify it's valid JSON
        parsed = json.loads(json_output)
        assert parsed['report_type'] == "daily_summary"
        assert len(parsed['sections']) == 1

    @pytest.mark.asyncio
    async def test_to_markdown(
        self,
        report_generator,
        sample_signals
    ):
        """Test converting report to Markdown"""
        report = await report_generator.generate_daily_summary(
            signals=sample_signals
        )

        markdown_output = report_generator.to_markdown(report)

        assert isinstance(markdown_output, str)
        assert markdown_output.startswith("# ")
        assert "## " in markdown_output  # Section headers
        assert "Trading Signals" in markdown_output

    @pytest.mark.asyncio
    async def test_to_html(
        self,
        report_generator,
        sample_signals
    ):
        """Test converting report to HTML"""
        report = await report_generator.generate_daily_summary(
            signals=sample_signals
        )

        html_output = report_generator.to_html(report)

        assert isinstance(html_output, str)
        assert "<html>" in html_output
        assert "<h1>" in html_output
        assert "<h2>" in html_output
        assert "</html>" in html_output
        assert "Trading Signals" in html_output

    @pytest.mark.asyncio
    async def test_markdown_formatting(self, report_generator):
        """Test Markdown output has proper structure"""
        report = await report_generator.generate_daily_summary()

        markdown = report_generator.to_markdown(report)

        lines = markdown.split('\n')
        # First line should be title
        assert lines[0].startswith("# Daily Summary")
        # Should have generated timestamp
        assert "Generated:" in markdown

    @pytest.mark.asyncio
    async def test_html_has_styles(self, report_generator):
        """Test HTML output includes CSS"""
        report = await report_generator.generate_daily_summary()

        html = report_generator.to_html(report)

        assert "<style>" in html
        assert "font-family" in html
        assert "</style>" in html


# ==================== SINGLETON PATTERN TESTS ====================

class TestSingleton:
    """Test singleton pattern"""

    def test_get_report_generator_creates_instance(self):
        """Test getting generator creates instance"""
        generator = get_report_generator()

        assert isinstance(generator, ReportGenerator)

    def test_get_report_generator_returns_same_instance(self):
        """Test getting generator returns cached instance"""
        gen1 = get_report_generator()
        gen2 = get_report_generator()

        # Should return same instance
        assert gen1 is gen2


# ==================== EDGE CASES ====================

class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_high_confidence_signals_limit(self, report_generator):
        """Test high confidence signals are limited to top 5"""
        # Create 10 high confidence signals
        signals = [
            {
                'symbol': f'STOCK{i}',
                'signal_type': 'BUY',
                'confidence_score': 0.8
            }
            for i in range(10)
        ]

        report = await report_generator.generate_daily_summary(signals=signals)

        content = report.sections[0].content
        # Should mention high confidence but only show top 5
        high_conf_section = content.split("High Confidence Signals")[1] if "High Confidence Signals" in content else ""
        stock_mentions = high_conf_section.count("STOCK")
        assert stock_mentions <= 5

    def test_trades_win_rate_calculation(self, report_generator):
        """Test win rate calculation is correct"""
        trades = [
            {'pnl': 100},
            {'pnl': -50},
            {'pnl': 200},
            {'pnl': -30}
        ]

        content = report_generator._format_trades_summary(trades)

        assert "Win Rate: 50" in content  # 2 wins out of 4 trades

    def test_empty_holdings(self, report_generator):
        """Test handling empty holdings"""
        content = report_generator._format_holdings({})

        assert "Symbol | Weight" in content

    def test_negative_returns_formatting(self, report_generator):
        """Test negative returns display correctly"""
        metrics = {'total_return': -5.5}

        content = report_generator._format_portfolio_metrics(metrics)

        assert "Total Return: ↓ 5.5%" in content

    def test_positive_returns_formatting(self, report_generator):
        """Test positive returns display correctly"""
        metrics = {'total_return': 5.5}

        content = report_generator._format_portfolio_metrics(metrics)

        assert "Total Return: ↑ 5.5%" in content
