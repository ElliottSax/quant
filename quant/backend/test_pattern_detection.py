"""
Test script for pattern detection system.

This script demonstrates the pattern detection capabilities by analyzing
several well-known stocks for cyclical patterns.
"""

import asyncio
from datetime import date, timedelta

from app.analysis.patterns import SARIMADetector, CalendarEffectsDetector


async def test_pattern_detection():
    """Test pattern detection on real market data."""

    print("=" * 80)
    print("PATTERN DETECTION SYSTEM TEST")
    print("=" * 80)
    print()

    # Test tickers (mix of large cap and small cap)
    test_tickers = [
        "SPY",   # S&P 500 ETF (market-wide patterns)
        "AAPL",  # Large cap tech
        "TSLA",  # Volatile growth stock
    ]

    # Initialize detectors
    print("Initializing detectors...")
    sarima_detector = SARIMADetector(
        min_seasonal_strength=0.3,
        min_occurrences=3,  # Lower for testing
        min_years=2.0,      # Lower for testing
        min_p_value=0.05,
        min_wfe=0.5,
    )

    calendar_detector = CalendarEffectsDetector(
        effects_to_test=['january', 'monday', 'turn_of_month'],
        min_occurrences=3,
        min_years=2.0,
        min_p_value=0.05,
        min_wfe=0.5,
    )

    print("✓ Detectors initialized")
    print()

    # Test date range (5 years of data)
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * 5)

    print(f"Analysis period: {start_date} to {end_date}")
    print()

    # Analyze each ticker
    all_results = []

    for ticker in test_tickers:
        print("=" * 80)
        print(f"ANALYZING: {ticker}")
        print("=" * 80)
        print()

        ticker_results = {
            'ticker': ticker,
            'sarima_patterns': [],
            'calendar_patterns': [],
            'errors': [],
        }

        # Test SARIMA detection
        print(f"Running SARIMA detector for {ticker}...")
        try:
            sarima_patterns = await sarima_detector.detect(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
            )

            ticker_results['sarima_patterns'] = sarima_patterns

            if sarima_patterns:
                print(f"✓ Found {len(sarima_patterns)} SARIMA patterns:")
                for pattern in sarima_patterns:
                    print(f"  - {pattern.name}")
                    print(f"    Reliability: {pattern.reliability_score:.1f}/100")
                    print(f"    Confidence: {pattern.confidence:.1f}%")
                    print(f"    Cycle: {pattern.cycle_length_days} days")
                    if pattern.validation_metrics:
                        print(f"    WFE: {pattern.validation_metrics.walk_forward_efficiency:.2f}")
                        print(f"    P-value: {pattern.validation_metrics.p_value:.4f}")
                        print(f"    Occurrences: {pattern.validation_metrics.sample_size}")
                    print()
            else:
                print(f"  No significant SARIMA patterns detected")
                print()

        except Exception as e:
            error_msg = f"SARIMA detection failed: {str(e)}"
            print(f"✗ {error_msg}")
            ticker_results['errors'].append(error_msg)
            print()

        # Test Calendar Effects detection
        print(f"Running Calendar Effects detector for {ticker}...")
        try:
            calendar_patterns = await calendar_detector.detect(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
            )

            ticker_results['calendar_patterns'] = calendar_patterns

            if calendar_patterns:
                print(f"✓ Found {len(calendar_patterns)} Calendar Effect patterns:")
                for pattern in calendar_patterns:
                    print(f"  - {pattern.name}")
                    print(f"    Reliability: {pattern.reliability_score:.1f}/100")
                    print(f"    Confidence: {pattern.confidence:.1f}%")
                    if pattern.validation_metrics:
                        print(f"    WFE: {pattern.validation_metrics.walk_forward_efficiency:.2f}")
                        print(f"    P-value: {pattern.validation_metrics.p_value:.4f}")
                        print(f"    Effect Size: {pattern.validation_metrics.effect_size:.3f}")
                    print()
            else:
                print(f"  No significant Calendar Effect patterns detected")
                print()

        except Exception as e:
            error_msg = f"Calendar Effects detection failed: {str(e)}"
            print(f"✗ {error_msg}")
            ticker_results['errors'].append(error_msg)
            print()

        all_results.append(ticker_results)
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    total_sarima = sum(len(r['sarima_patterns']) for r in all_results)
    total_calendar = sum(len(r['calendar_patterns']) for r in all_results)
    total_errors = sum(len(r['errors']) for r in all_results)

    print(f"Tickers analyzed: {len(test_tickers)}")
    print(f"SARIMA patterns detected: {total_sarima}")
    print(f"Calendar Effect patterns detected: {total_calendar}")
    print(f"Total patterns: {total_sarima + total_calendar}")
    print(f"Errors: {total_errors}")
    print()

    # Show top patterns by reliability
    all_patterns = []
    for result in all_results:
        all_patterns.extend(result['sarima_patterns'])
        all_patterns.extend(result['calendar_patterns'])

    if all_patterns:
        all_patterns.sort(key=lambda p: p.reliability_score, reverse=True)

        print("TOP 5 PATTERNS BY RELIABILITY:")
        print()
        for i, pattern in enumerate(all_patterns[:5], 1):
            print(f"{i}. {pattern.name}")
            print(f"   Reliability: {pattern.reliability_score:.1f}/100")
            print(f"   Confidence: {pattern.confidence:.1f}%")
            print(f"   Type: {pattern.pattern_type.value}")
            if pattern.validation_metrics:
                print(f"   WFE: {pattern.validation_metrics.walk_forward_efficiency:.2f}")
            print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

    return all_results


if __name__ == "__main__":
    print()
    print("Starting pattern detection test...")
    print()

    results = asyncio.run(test_pattern_detection())

    print()
    print("Test completed successfully!")
    print()

    # Show how to access results
    print("Results structure:")
    print(f"- Analyzed {len(results)} tickers")
    for result in results:
        ticker = result['ticker']
        n_sarima = len(result['sarima_patterns'])
        n_calendar = len(result['calendar_patterns'])
        print(f"  {ticker}: {n_sarima} SARIMA + {n_calendar} Calendar = {n_sarima + n_calendar} total patterns")
