"""
Automated Reporting Service

Generate and distribute automated reports for trading analysis.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel
import json


class ReportType(str, Enum):
    """Report types"""
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_PERFORMANCE = "weekly_performance"
    MONTHLY_ANALYSIS = "monthly_analysis"
    PORTFOLIO_SNAPSHOT = "portfolio_snapshot"
    SIGNAL_SUMMARY = "signal_summary"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """Report output formats"""
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    TEXT = "text"


class ReportSection(BaseModel):
    """Report section"""
    title: str
    content: str
    data: Optional[Dict] = None


class Report(BaseModel):
    """Generated report"""
    report_id: str
    report_type: ReportType
    title: str
    generated_at: datetime
    sections: List[ReportSection]
    metadata: Dict = {}


class ReportGenerator:
    """
    Generate automated trading reports

    Creates comprehensive reports with:
    - Performance summaries
    - Signal analysis
    - Portfolio metrics
    - Market insights
    """

    async def generate_daily_summary(
        self,
        signals: List[Dict] = None,
        portfolio_metrics: Optional[Dict] = None,
        market_data: Optional[Dict] = None
    ) -> Report:
        """
        Generate daily summary report

        Args:
            signals: Recent trading signals
            portfolio_metrics: Portfolio performance
            market_data: Market overview

        Returns:
            Daily summary report
        """
        sections = []

        # Market Overview Section
        if market_data:
            market_content = self._format_market_overview(market_data)
            sections.append(ReportSection(
                title="Market Overview",
                content=market_content,
                data=market_data
            ))

        # Signals Section
        if signals:
            signals_content = self._format_signals_summary(signals)
            sections.append(ReportSection(
                title="Trading Signals",
                content=signals_content,
                data={"signals": signals, "count": len(signals)}
            ))

        # Portfolio Section
        if portfolio_metrics:
            portfolio_content = self._format_portfolio_metrics(portfolio_metrics)
            sections.append(ReportSection(
                title="Portfolio Performance",
                content=portfolio_content,
                data=portfolio_metrics
            ))

        report = Report(
            report_id=f"daily_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            report_type=ReportType.DAILY_SUMMARY,
            title=f"Daily Summary - {datetime.utcnow().strftime('%Y-%m-%d')}",
            generated_at=datetime.utcnow(),
            sections=sections,
            metadata={
                "signals_count": len(signals) if signals else 0,
                "has_portfolio": portfolio_metrics is not None
            }
        )

        return report

    async def generate_weekly_performance(
        self,
        trades: List[Dict] = None,
        returns: Optional[Dict] = None,
        benchmarks: Optional[Dict] = None
    ) -> Report:
        """Generate weekly performance report"""
        sections = []

        # Returns Section
        if returns:
            returns_content = self._format_returns_analysis(returns)
            sections.append(ReportSection(
                title="Weekly Returns",
                content=returns_content,
                data=returns
            ))

        # Trades Section
        if trades:
            trades_content = self._format_trades_summary(trades)
            sections.append(ReportSection(
                title="Trading Activity",
                content=trades_content,
                data={"trades": trades, "count": len(trades)}
            ))

        # Benchmark Comparison
        if benchmarks:
            benchmark_content = self._format_benchmark_comparison(benchmarks)
            sections.append(ReportSection(
                title="Benchmark Comparison",
                content=benchmark_content,
                data=benchmarks
            ))

        report = Report(
            report_id=f"weekly_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            report_type=ReportType.WEEKLY_PERFORMANCE,
            title=f"Weekly Performance - Week of {datetime.utcnow().strftime('%Y-%m-%d')}",
            generated_at=datetime.utcnow(),
            sections=sections,
            metadata={
                "trades_count": len(trades) if trades else 0
            }
        )

        return report

    async def generate_portfolio_snapshot(
        self,
        holdings: Dict[str, float],
        performance: Dict,
        risk_metrics: Dict
    ) -> Report:
        """Generate portfolio snapshot report"""
        sections = []

        # Holdings
        holdings_content = self._format_holdings(holdings)
        sections.append(ReportSection(
            title="Current Holdings",
            content=holdings_content,
            data=holdings
        ))

        # Performance
        perf_content = self._format_performance(performance)
        sections.append(ReportSection(
            title="Performance Metrics",
            content=perf_content,
            data=performance
        ))

        # Risk
        risk_content = self._format_risk_metrics(risk_metrics)
        sections.append(ReportSection(
            title="Risk Analysis",
            content=risk_content,
            data=risk_metrics
        ))

        report = Report(
            report_id=f"portfolio_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            report_type=ReportType.PORTFOLIO_SNAPSHOT,
            title=f"Portfolio Snapshot - {datetime.utcnow().strftime('%Y-%m-%d')}",
            generated_at=datetime.utcnow(),
            sections=sections,
            metadata={
                "num_holdings": len(holdings)
            }
        )

        return report

    def _format_market_overview(self, data: Dict) -> str:
        """Format market overview section"""
        lines = []
        lines.append(f"Market Status: {data.get('status', 'Unknown')}")

        if 'indices' in data:
            lines.append("\nMajor Indices:")
            for index, value in data['indices'].items():
                change = value.get('change_percent', 0)
                arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
                lines.append(f"  {index}: {value.get('price', 0):.2f} {arrow} {abs(change):.2f}%")

        return "\n".join(lines)

    def _format_signals_summary(self, signals: List[Dict]) -> str:
        """Format signals section"""
        if not signals:
            return "No signals generated today"

        lines = []
        lines.append(f"Total Signals: {len(signals)}\n")

        # Group by signal type
        by_type = {}
        for signal in signals:
            sig_type = signal.get('signal_type', 'unknown')
            by_type[sig_type] = by_type.get(sig_type, 0) + 1

        lines.append("Signal Distribution:")
        for sig_type, count in sorted(by_type.items()):
            lines.append(f"  {sig_type}: {count}")

        # High confidence signals
        high_conf = [s for s in signals if s.get('confidence_score', 0) > 0.7]
        if high_conf:
            lines.append(f"\nHigh Confidence Signals ({len(high_conf)}):")
            for signal in high_conf[:5]:  # Top 5
                lines.append(f"  {signal.get('symbol')}: {signal.get('signal_type')} ({signal.get('confidence_score', 0)*100:.0f}%)")

        return "\n".join(lines)

    def _format_portfolio_metrics(self, metrics: Dict) -> str:
        """Format portfolio metrics"""
        lines = []

        if 'total_return' in metrics:
            ret = metrics['total_return']
            arrow = "↑" if ret > 0 else "↓"
            lines.append(f"Total Return: {arrow} {abs(ret):.2f}%")

        if 'sharpe_ratio' in metrics:
            lines.append(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")

        if 'max_drawdown' in metrics:
            lines.append(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")

        if 'volatility' in metrics:
            lines.append(f"Volatility: {metrics['volatility']:.2f}%")

        return "\n".join(lines) if lines else "No metrics available"

    def _format_returns_analysis(self, returns: Dict) -> str:
        """Format returns analysis"""
        lines = []

        if 'weekly_return' in returns:
            ret = returns['weekly_return']
            arrow = "↑" if ret > 0 else "↓"
            lines.append(f"Weekly Return: {arrow} {abs(ret):.2f}%")

        if 'mtd_return' in returns:
            lines.append(f"Month-to-Date: {returns['mtd_return']:.2f}%")

        if 'ytd_return' in returns:
            lines.append(f"Year-to-Date: {returns['ytd_return']:.2f}%")

        return "\n".join(lines)

    def _format_trades_summary(self, trades: List[Dict]) -> str:
        """Format trades summary"""
        if not trades:
            return "No trades this week"

        wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
        losses = len(trades) - wins
        total_pnl = sum(t.get('pnl', 0) for t in trades)

        lines = [
            f"Total Trades: {len(trades)}",
            f"Winning: {wins}",
            f"Losing: {losses}",
            f"Win Rate: {(wins/len(trades)*100):.1f}%",
            f"Total P&L: ${total_pnl:.2f}"
        ]

        return "\n".join(lines)

    def _format_benchmark_comparison(self, benchmarks: Dict) -> str:
        """Format benchmark comparison"""
        lines = []

        for benchmark, data in benchmarks.items():
            return_val = data.get('return', 0)
            alpha = data.get('alpha', 0)
            beta = data.get('beta', 0)

            lines.append(f"{benchmark}:")
            lines.append(f"  Return: {return_val:.2f}%")
            lines.append(f"  Alpha: {alpha:.2f}%")
            lines.append(f"  Beta: {beta:.2f}")

        return "\n".join(lines) if lines else "No benchmark data"

    def _format_holdings(self, holdings: Dict[str, float]) -> str:
        """Format holdings"""
        lines = ["Symbol | Weight"]
        lines.append("-" * 20)

        for symbol, weight in sorted(holdings.items(), key=lambda x: -x[1]):
            lines.append(f"{symbol:6} | {weight*100:>5.1f}%")

        return "\n".join(lines)

    def _format_performance(self, performance: Dict) -> str:
        """Format performance metrics"""
        return self._format_portfolio_metrics(performance)

    def _format_risk_metrics(self, risk: Dict) -> str:
        """Format risk metrics"""
        lines = []

        if 'var_95' in risk:
            lines.append(f"VaR (95%): {risk['var_95']:.2f}%")

        if 'cvar_95' in risk:
            lines.append(f"CVaR (95%): {risk['cvar_95']:.2f}%")

        if 'beta' in risk:
            lines.append(f"Market Beta: {risk['beta']:.2f}")

        if 'correlation' in risk:
            lines.append(f"Market Correlation: {risk['correlation']:.2f}")

        return "\n".join(lines) if lines else "No risk data"

    def to_json(self, report: Report) -> str:
        """Convert report to JSON"""
        return report.json(indent=2)

    def to_markdown(self, report: Report) -> str:
        """Convert report to Markdown"""
        lines = []
        lines.append(f"# {report.title}")
        lines.append(f"\n*Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}*\n")

        for section in report.sections:
            lines.append(f"## {section.title}\n")
            lines.append(section.content)
            lines.append("\n")

        return "\n".join(lines)

    def to_html(self, report: Report) -> str:
        """Convert report to HTML"""
        html = f"""
        <html>
        <head>
            <title>{report.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
                .metadata {{ color: #999; font-size: 0.9em; }}
                pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>{report.title}</h1>
            <p class="metadata">Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}</p>
        """

        for section in report.sections:
            html += f"<h2>{section.title}</h2>"
            html += f"<pre>{section.content}</pre>"

        html += "</body></html>"
        return html


# Global instance
_report_generator: Optional[ReportGenerator] = None


def get_report_generator() -> ReportGenerator:
    """Get or create report generator instance"""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator
