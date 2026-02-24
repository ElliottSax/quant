#!/usr/bin/env python3
"""
Standalone Stock Prediction Demo

Works without backend setup - uses libraries directly.
Perfect for quick testing and demonstrations.
"""

import asyncio
import yfinance as yf
import pandas as pd
import numpy as np


def calculate_rsi(prices, period=14):
    """Calculate RSI indicator."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD indicator."""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands."""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower


def generate_signals(df):
    """Generate trading signals from indicators."""
    signals = {}

    # Calculate indicators
    close = df['Close']
    rsi = calculate_rsi(close)
    macd, signal_line, histogram = calculate_macd(close)
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close)
    sma_20 = close.rolling(20).mean()
    sma_50 = close.rolling(50).mean()

    # Get current values
    current_rsi = rsi.iloc[-1]
    current_macd = macd.iloc[-1]
    current_signal = signal_line.iloc[-1]
    current_price = close.iloc[-1]

    # RSI Signal
    if current_rsi < 30:
        signals['rsi'] = 'BUY'
        signals['rsi_value'] = current_rsi
        signals['rsi_reason'] = f'Oversold (RSI: {current_rsi:.1f})'
    elif current_rsi > 70:
        signals['rsi'] = 'SELL'
        signals['rsi_value'] = current_rsi
        signals['rsi_reason'] = f'Overbought (RSI: {current_rsi:.1f})'
    else:
        signals['rsi'] = 'HOLD'
        signals['rsi_value'] = current_rsi
        signals['rsi_reason'] = f'Neutral (RSI: {current_rsi:.1f})'

    # MACD Signal
    if current_macd > current_signal:
        signals['macd'] = 'BUY'
        signals['macd_reason'] = 'MACD above signal'
    else:
        signals['macd'] = 'SELL'
        signals['macd_reason'] = 'MACD below signal'

    # MA Crossover
    if not pd.isna(sma_20.iloc[-1]) and not pd.isna(sma_50.iloc[-1]):
        if sma_20.iloc[-1] > sma_50.iloc[-1]:
            signals['ma'] = 'BUY'
            signals['ma_reason'] = 'SMA20 > SMA50 (uptrend)'
        else:
            signals['ma'] = 'SELL'
            signals['ma_reason'] = 'SMA20 < SMA50 (downtrend)'

    # Bollinger Bands
    if current_price < bb_lower.iloc[-1]:
        signals['bb'] = 'BUY'
        signals['bb_reason'] = 'Price below lower band'
    elif current_price > bb_upper.iloc[-1]:
        signals['bb'] = 'SELL'
        signals['bb_reason'] = 'Price above upper band'
    else:
        signals['bb'] = 'HOLD'
        signals['bb_reason'] = 'Price within bands'

    # Overall Signal (majority vote)
    buy_count = sum(1 for k in ['rsi', 'macd', 'ma', 'bb'] if signals.get(k) == 'BUY')
    sell_count = sum(1 for k in ['rsi', 'macd', 'ma', 'bb'] if signals.get(k) == 'SELL')

    if buy_count > sell_count:
        signals['overall'] = 'BUY'
        signals['overall_confidence'] = buy_count / 4
    elif sell_count > buy_count:
        signals['overall'] = 'SELL'
        signals['overall_confidence'] = sell_count / 4
    else:
        signals['overall'] = 'HOLD'
        signals['overall_confidence'] = 0.5

    return signals, {
        'rsi': current_rsi,
        'macd': current_macd,
        'macd_signal': current_signal,
        'bb_upper': bb_upper.iloc[-1],
        'bb_middle': bb_middle.iloc[-1],
        'bb_lower': bb_lower.iloc[-1],
        'sma_20': sma_20.iloc[-1],
        'sma_50': sma_50.iloc[-1],
    }


def main():
    """Run the demo."""
    symbol = "AAPL"

    print("=" * 60)
    print(f"Stock Prediction Demo - {symbol}")
    print("=" * 60)
    print()

    # Fetch data
    print(f"📊 Fetching data for {symbol}...")
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1y", interval="1d")

    if df.empty:
        print(f"❌ No data found for {symbol}")
        return 1

    print(f"✅ Fetched {len(df)} days of data")
    print()

    # Display current price info
    current_price = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    change = current_price - prev_close
    change_pct = (change / prev_close) * 100

    print(f"💰 Current Price: ${current_price:.2f}")
    print(f"   Change: ${change:.2f} ({change_pct:+.2f}%)")
    print(f"   Volume: {df['Volume'].iloc[-1]:,.0f}")
    print()

    # Generate signals
    print("🎯 Calculating Technical Indicators...")
    signals, indicators = generate_signals(df)
    print("✅ Analysis complete")
    print()

    # Display indicators
    print("=" * 60)
    print("📈 Technical Indicators")
    print("=" * 60)
    print(f"  RSI (14):        {indicators['rsi']:.2f}")
    print(f"  MACD:            {indicators['macd']:.3f}")
    print(f"  MACD Signal:     {indicators['macd_signal']:.3f}")
    print(f"  SMA 20:          ${indicators['sma_20']:.2f}")
    print(f"  SMA 50:          ${indicators['sma_50']:.2f}")
    print(f"  BB Upper:        ${indicators['bb_upper']:.2f}")
    print(f"  BB Middle:       ${indicators['bb_middle']:.2f}")
    print(f"  BB Lower:        ${indicators['bb_lower']:.2f}")
    print()

    # Display signals
    print("=" * 60)
    print("🎯 Trading Signals")
    print("=" * 60)

    def get_emoji(signal):
        return "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"

    print(f"  {get_emoji(signals['rsi'])} RSI:         {signals['rsi']}")
    print(f"     → {signals['rsi_reason']}")
    print()
    print(f"  {get_emoji(signals['macd'])} MACD:        {signals['macd']}")
    print(f"     → {signals['macd_reason']}")
    print()
    print(f"  {get_emoji(signals['ma'])} MA Cross:    {signals['ma']}")
    print(f"     → {signals['ma_reason']}")
    print()
    print(f"  {get_emoji(signals['bb'])} Bollinger:   {signals['bb']}")
    print(f"     → {signals['bb_reason']}")
    print()

    # Overall recommendation
    print("=" * 60)
    print("🎪 OVERALL RECOMMENDATION")
    print("=" * 60)
    overall = signals['overall']
    confidence = signals['overall_confidence']
    confidence_tier = "HIGH" if confidence >= 0.7 else "MEDIUM" if confidence >= 0.5 else "LOW"

    print(f"  Signal:      {get_emoji(overall)} {overall}")
    print(f"  Confidence:  {confidence:.1%} ({confidence_tier})")
    print()

    if overall == "BUY":
        print("  💡 Interpretation: Multiple indicators suggest bullish momentum.")
        print("     Consider opening a long position with proper risk management.")
    elif overall == "SELL":
        print("  💡 Interpretation: Multiple indicators suggest bearish momentum.")
        print("     Consider closing long positions or opening shorts.")
    else:
        print("  💡 Interpretation: Mixed signals. Market may be consolidating.")
        print("     Wait for clearer signals before taking action.")
    print()

    # Risk management
    print("=" * 60)
    print("💰 Risk Management Example")
    print("=" * 60)
    portfolio_value = 100000
    risk_per_trade = 0.02
    stop_loss_pct = 0.05

    stop_loss_price = current_price * (1 - stop_loss_pct) if overall == "BUY" else current_price * (1 + stop_loss_pct)
    risk_amount = portfolio_value * risk_per_trade
    risk_per_share = abs(current_price - stop_loss_price)
    shares = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
    position_value = shares * current_price

    print(f"  Portfolio Value:    ${portfolio_value:,.0f}")
    print(f"  Risk per Trade:     {risk_per_trade:.1%}")
    print(f"  Entry Price:        ${current_price:.2f}")
    print(f"  Stop Loss:          ${stop_loss_price:.2f}")
    print()
    print(f"  Recommended Shares: {shares:,}")
    print(f"  Position Value:     ${position_value:,.2f}")
    print(f"  Risk Amount:        ${risk_amount:,.2f}")
    print(f"  % of Portfolio:     {(position_value / portfolio_value * 100):.2f}%")
    print()

    # Support/Resistance
    print("=" * 60)
    print("📏 Support & Resistance (Last 20 days)")
    print("=" * 60)
    recent = df.tail(20)
    support = recent['Low'].min()
    resistance = recent['High'].max()

    print(f"  Current:     ${current_price:.2f}")
    print(f"  Support:     ${support:.2f} ({((current_price - support) / current_price * 100):.2f}% away)")
    print(f"  Resistance:  ${resistance:.2f} ({((resistance - current_price) / current_price * 100):.2f}% away)")
    print()

    # Summary
    print("=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)
    print()
    print("📝 Next Steps:")
    print("  • Review the signals and indicators above")
    print("  • Consider your own analysis and risk tolerance")
    print("  • Use proper position sizing and stop losses")
    print("  • Try other symbols: python standalone_demo.py TSLA")
    print()
    print("⚠️  Disclaimer: This is for educational purposes only.")
    print("    Not financial advice. Do your own research!")
    print()

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
