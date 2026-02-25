"""
Python Client Example for Quant Backtesting API
Demonstrates how to use the demo endpoints
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class QuantBacktestClient:
    """Client for Quant Backtesting Demo API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize client
        
        Args:
            base_url: API base URL (e.g., "https://your-app.railway.app")
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def list_strategies(self) -> List[Dict]:
        """List available demo strategies"""
        response = requests.get(f"{self.api_base}/backtesting/demo/strategies")
        response.raise_for_status()
        return response.json()
    
    def run_backtest(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        strategy: str = "ma_crossover",
        initial_capital: float = 100000,
        strategy_params: Optional[Dict] = None
    ) -> Dict:
        """
        Run a backtest
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            start_date: Start date for backtest
            end_date: End date for backtest
            strategy: Strategy name (from list_strategies)
            initial_capital: Starting capital in dollars
            strategy_params: Optional strategy parameters
        
        Returns:
            Backtest results with performance metrics
        """
        payload = {
            "symbol": symbol,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "strategy": strategy,
            "initial_capital": initial_capital,
            "strategy_params": strategy_params or {}
        }
        
        response = requests.post(
            f"{self.api_base}/backtesting/demo/run",
            json=payload,
            timeout=60  # Backtests can take time
        )
        response.raise_for_status()
        return response.json()
    
    def compare_strategies(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        strategies: List[str],
        initial_capital: float = 100000
    ) -> Dict[str, Dict]:
        """
        Compare multiple strategies
        
        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            strategies: List of strategy names
            initial_capital: Starting capital
        
        Returns:
            Dictionary mapping strategy names to results
        """
        results = {}
        for strategy in strategies:
            try:
                result = self.run_backtest(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    strategy=strategy,
                    initial_capital=initial_capital
                )
                results[strategy] = result
            except requests.HTTPError as e:
                print(f"Error running {strategy}: {e}")
                results[strategy] = {"error": str(e)}
        
        return results


def main():
    """Example usage"""
    
    # Initialize client
    # Change to your Railway URL after deployment
    client = QuantBacktestClient("https://your-app.railway.app")
    
    # Check API health
    print("Checking API health...")
    health = client.health_check()
    print(f"✅ API Status: {health['status']}")
    print()
    
    # List available strategies
    print("Available strategies:")
    strategies = client.list_strategies()
    for strategy in strategies:
        print(f"  - {strategy['name']}: {strategy['description']}")
    print()
    
    # Run a backtest
    print("Running backtest for AAPL...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 6 months
    
    result = client.run_backtest(
        symbol="AAPL",
        start_date=start_date,
        end_date=end_date,
        strategy="ma_crossover",
        initial_capital=100000,
        strategy_params={
            "fast_period": 20,
            "slow_period": 50
        }
    )
    
    print(f"✅ Backtest complete!")
    print(f"  Total Return: {result['total_return']:.2f}%")
    print(f"  Sharpe Ratio: {result['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown: {result['max_drawdown']:.2f}%")
    print(f"  Total Trades: {result['total_trades']}")
    print(f"  Win Rate: {result['win_rate']:.2f}%")
    print()
    
    # Compare multiple strategies
    print("Comparing strategies...")
    comparison = client.compare_strategies(
        symbol="AAPL",
        start_date=start_date,
        end_date=end_date,
        strategies=["ma_crossover", "rsi_strategy", "bollinger_bands"]
    )
    
    print("Strategy Comparison:")
    for strategy_name, result in comparison.items():
        if "error" not in result:
            print(f"  {strategy_name}:")
            print(f"    Return: {result['total_return']:.2f}%")
            print(f"    Sharpe: {result['sharpe_ratio']:.2f}")


if __name__ == "__main__":
    main()
