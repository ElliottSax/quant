#!/usr/bin/env python3
"""
Stock Prediction Demo Script

Demonstrates how to use the prediction API programmatically.
Shows examples of:
- Fetching market data
- Calculating technical indicators
- Detecting patterns
- Generating trading signals
- Using pre-built strategies

Usage:
    python prediction_demo.py AAPL
    python prediction_demo.py TSLA --strategy ensemble
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "quant" / "backend"))

from app.services.market_data import MarketDataClient
from app.services.technical_analysis import IndicatorCalculator, PatternDetector
from app.services.prediction import StrategyFactory, PredictionHelpers


async def demo_market_data(symbol: str):
    """Demonstrate market data fetching."""
    print(f"\n{'='*60}")
    print(f"📊 Market Data Demo for {symbol}")
    print(f"{'='*60}\n")

    client = MarketDataClient()

    try:
        # Fetch historical data
        print("Fetching 1 year of daily data...")
        df = await client.get_historical_data(symbol, period="1y", interval="1d")
        print(f"✅ Fetched {len(df)} days of data")
        print(f"\nLatest prices:")
        print(df.tail()[['Open', 'High', 'Low', 'Close', 'Volume']])

        # Get current quote
        print(f"\nFetching current quote...")
        quote = await client.get_quote(symbol)
        print(f"✅ Current price: ${quote.get('price', 'N/A')}")
        print(f"   Change: {quote.get('change', 'N/A')} ({quote.get('change_percent', 'N/A')}%)")
        print(f"   Volume: {quote.get('volume', 'N/A'):,}")

        return df

    finally:
        await client.close()


async def demo_technical_indicators(symbol: str, df):
    """Demonstrate technical indicator calculation."""
    print(f"\n{'='*60}")
    print(f"📈 Technical Indicators Demo")
    print(f"{'='*60}\n")

    calc = IndicatorCalculator()

    # Calculate all indicators
    print("Calculating 50+ technical indicators...")
    indicators = calc.calculate_all(df)
    print("✅ Indicators calculated\n")

    # Display current values
    current = indicators['current']
    print("Current Indicator Values:")
    print(f"  RSI: {current.get('rsi', 'N/A'):.2f}" if current.get('rsi') else "  RSI: N/A")
    print(f"  MACD: {current.get('macd', 'N/A'):.3f}" if current.get('macd') else "  MACD: N/A")
    print(f"  Signal: {current.get('macd_signal', 'N/A'):.3f}" if current.get('macd_signal') else "  Signal: N/A")
    print(f"  BB Upper: ${current.get('bb_upper', 'N/A'):.2f}" if current.get('bb_upper') else "  BB Upper: N/A")
    print(f"  BB Lower: ${current.get('bb_lower', 'N/A'):.2f}" if current.get('bb_lower') else "  BB Lower: N/A")
    print(f"  SMA 20: ${current.get('sma_20', 'N/A'):.2f}" if current.get('sma_20') else "  SMA 20: N/A")
    print(f"  SMA 50: ${current.get('sma_50', 'N/A'):.2f}" if current.get('sma_50') else "  SMA 50: N/A")

    # Display signals
    print("\nTechnical Signals:")
    signals = indicators['signals']
    for name, signal in signals.items():
        emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
        print(f"  {emoji} {name.upper()}: {signal}")

    return indicators


async def demo_pattern_detection(symbol: str, df):
    """Demonstrate pattern detection."""
    print(f"\n{'='*60}")
    print(f"🕯️  Pattern Detection Demo")
    print(f"{'='*60}\n")

    detector = PatternDetector()

    print("Scanning for candlestick patterns...")
    patterns = detector.detect_all_patterns(df)
    print("✅ Scan complete\n")

    # Display current patterns
    if patterns['current']:
        print(f"Patterns detected in latest candle:")
        for pattern in patterns['current']:
            emoji = "🟢" if pattern['direction'] == 'bullish' else "🔴" if pattern['direction'] == 'bearish' else "⚪"
            print(f"  {emoji} {pattern['name']} ({pattern['strength']}, {pattern['direction']})")
    else:
        print("No patterns detected in latest candle")

    # Display recent patterns
    if patterns['recent']:
        print(f"\nRecent patterns (last 10 days):")
        for pattern in patterns['recent'][:5]:  # Show first 5
            print(f"  • {pattern['name']} ({pattern['strength']})")

    return patterns


async def demo_trading_strategies(symbol: str, df, indicators, strategy_name: str = "ensemble"):
    """Demonstrate trading strategies."""
    print(f"\n{'='*60}")
    print(f"🎯 Trading Strategy Demo")
    print(f"{'='*60}\n")

    # Create strategy
    print(f"Using strategy: {strategy_name}")
    strategy = StrategyFactory.create_strategy(strategy_name)

    # Generate signal
    print("Generating trading signal...")
    signal_result = strategy.generate_signal(df, indicators)
    print("✅ Signal generated\n")

    # Display result
    signal = signal_result['signal']
    confidence = signal_result['confidence']
    reasoning = signal_result['reasoning']

    emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
    print(f"{emoji} Signal: {signal}")
    print(f"   Confidence: {confidence:.1%} ({PredictionHelpers.calculate_confidence_tier(confidence)})")
    print(f"   Reasoning: {reasoning}")

    # Display additional details
    if 'individual_signals' in signal_result:
        print("\n   Individual Strategy Signals:")
        for strat_name, strat_signal in signal_result['individual_signals'].items():
            strat_conf = signal_result['individual_confidences'][strat_name]
            emoji = "🟢" if strat_signal == "BUY" else "🔴" if strat_signal == "SELL" else "⚪"
            print(f"     {emoji} {strat_name}: {strat_signal} ({strat_conf:.1%})")

    return signal_result


async def demo_position_sizing(symbol: str, df, signal_result):
    """Demonstrate position sizing calculation."""
    if signal_result['signal'] == "HOLD":
        return

    print(f"\n{'='*60}")
    print(f"💰 Position Sizing Demo")
    print(f"{'='*60}\n")

    current_price = float(df['Close'].iloc[-1])
    portfolio_value = 100000  # $100k portfolio
    risk_per_trade = 0.02  # 2% risk per trade

    # Calculate stop loss (simple: 5% below entry for BUY, 5% above for SELL)
    if signal_result['signal'] == "BUY":
        stop_loss = current_price * 0.95
    else:
        stop_loss = current_price * 1.05

    position = PredictionHelpers.calculate_position_size(
        portfolio_value=portfolio_value,
        risk_per_trade=risk_per_trade,
        entry_price=current_price,
        stop_loss_price=stop_loss
    )

    print(f"Portfolio Value: ${portfolio_value:,.0f}")
    print(f"Risk per Trade: {risk_per_trade:.1%}")
    print(f"Entry Price: ${current_price:.2f}")
    print(f"Stop Loss: ${stop_loss:.2f}")
    print(f"\nRecommended Position:")
    print(f"  Shares: {position['shares']:,}")
    print(f"  Position Value: ${position['position_value']:,.2f}")
    print(f"  Risk Amount: ${position['risk_amount']:,.2f}")
    print(f"  % of Portfolio: {position['percentage_of_portfolio']:.2f}%")


async def demo_support_resistance(symbol: str, df):
    """Demonstrate support/resistance calculation."""
    print(f"\n{'='*60}")
    print(f"📏 Support & Resistance Demo")
    print(f"{'='*60}\n")

    levels = PredictionHelpers.calculate_support_resistance(df, window=20)

    print(f"Current Price: ${levels['current']:.2f}")
    print(f"Support Level: ${levels['support']:.2f} ({levels['distance_to_support']:.2f}% away)")
    print(f"Resistance Level: ${levels['resistance']:.2f} ({levels['distance_to_resistance']:.2f}% away)")


async def main():
    """Run all demos."""
    # Get symbol from command line
    if len(sys.argv) < 2:
        symbol = "AAPL"
        print(f"No symbol provided, using default: {symbol}")
    else:
        symbol = sys.argv[1].upper()

    # Get strategy from command line
    strategy_name = "ensemble"
    if len(sys.argv) > 2 and sys.argv[2] == "--strategy":
        strategy_name = sys.argv[3] if len(sys.argv) > 3 else "ensemble"

    print(f"\n{'#'*60}")
    print(f"# Stock Prediction Demo")
    print(f"# Symbol: {symbol}")
    print(f"# Strategy: {strategy_name}")
    print(f"{'#'*60}")

    try:
        # Run demos
        df = await demo_market_data(symbol)
        indicators = await demo_technical_indicators(symbol, df)
        patterns = await demo_pattern_detection(symbol, df)
        signal_result = await demo_trading_strategies(symbol, df, indicators, strategy_name)
        await demo_position_sizing(symbol, df, signal_result)
        await demo_support_resistance(symbol, df)

        # Summary
        print(f"\n{'='*60}")
        print(f"✅ Demo Complete!")
        print(f"{'='*60}\n")

        print("Next steps:")
        print("  1. Try different symbols: python prediction_demo.py TSLA")
        print("  2. Try different strategies: python prediction_demo.py AAPL --strategy rsi")
        print("  3. Available strategies: rsi, macd, ma_crossover, bollinger, ensemble")
        print("  4. Check API docs: http://localhost:8000/api/v1/docs")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
