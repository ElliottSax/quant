/**
 * JavaScript Client Example for Quant Backtesting API
 * Works in Node.js and browsers
 */

class QuantBacktestClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiBase = `${this.baseUrl}/api/v1`;
  }

  /**
   * Check API health
   */
  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) throw new Error(`Health check failed: ${response.statusText}`);
    return response.json();
  }

  /**
   * List available demo strategies
   */
  async listStrategies() {
    const response = await fetch(`${this.apiBase}/backtesting/demo/strategies`);
    if (!response.ok) throw new Error(`Failed to list strategies: ${response.statusText}`);
    return response.json();
  }

  /**
   * Run a backtest
   * 
   * @param {Object} params - Backtest parameters
   * @param {string} params.symbol - Stock symbol (e.g., "AAPL")
   * @param {Date} params.startDate - Start date
   * @param {Date} params.endDate - End date
   * @param {string} params.strategy - Strategy name
   * @param {number} params.initialCapital - Starting capital
   * @param {Object} params.strategyParams - Optional strategy parameters
   */
  async runBacktest({
    symbol,
    startDate,
    endDate,
    strategy = 'ma_crossover',
    initialCapital = 100000,
    strategyParams = {}
  }) {
    const payload = {
      symbol,
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      strategy,
      initial_capital: initialCapital,
      strategy_params: strategyParams
    };

    const response = await fetch(`${this.apiBase}/backtesting/demo/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Backtest failed');
    }

    return response.json();
  }

  /**
   * Compare multiple strategies
   */
  async compareStrategies({
    symbol,
    startDate,
    endDate,
    strategies,
    initialCapital = 100000
  }) {
    const results = {};

    for (const strategy of strategies) {
      try {
        const result = await this.runBacktest({
          symbol,
          startDate,
          endDate,
          strategy,
          initialCapital
        });
        results[strategy] = result;
      } catch (error) {
        console.error(`Error running ${strategy}:`, error);
        results[strategy] = { error: error.message };
      }
    }

    return results;
  }
}


// Example usage
async function main() {
  // Initialize client
  // Change to your Railway URL after deployment
  const client = new QuantBacktestClient('https://your-app.railway.app');

  try {
    // Check API health
    console.log('Checking API health...');
    const health = await client.healthCheck();
    console.log(`✅ API Status: ${health.status}\n`);

    // List available strategies
    console.log('Available strategies:');
    const strategies = await client.listStrategies();
    strategies.forEach(strategy => {
      console.log(`  - ${strategy.name}: ${strategy.description}`);
    });
    console.log('');

    // Run a backtest
    console.log('Running backtest for AAPL...');
    const endDate = new Date();
    const startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 6); // 6 months ago

    const result = await client.runBacktest({
      symbol: 'AAPL',
      startDate,
      endDate,
      strategy: 'ma_crossover',
      initialCapital: 100000,
      strategyParams: {
        fast_period: 20,
        slow_period: 50
      }
    });

    console.log('✅ Backtest complete!');
    console.log(`  Total Return: ${result.total_return.toFixed(2)}%`);
    console.log(`  Sharpe Ratio: ${result.sharpe_ratio.toFixed(2)}`);
    console.log(`  Max Drawdown: ${result.max_drawdown.toFixed(2)}%`);
    console.log(`  Total Trades: ${result.total_trades}`);
    console.log(`  Win Rate: ${result.win_rate.toFixed(2)}%\n`);

    // Compare multiple strategies
    console.log('Comparing strategies...');
    const comparison = await client.compareStrategies({
      symbol: 'AAPL',
      startDate,
      endDate,
      strategies: ['ma_crossover', 'rsi_strategy', 'bollinger_bands']
    });

    console.log('Strategy Comparison:');
    for (const [strategyName, stratResult] of Object.entries(comparison)) {
      if (!stratResult.error) {
        console.log(`  ${strategyName}:`);
        console.log(`    Return: ${stratResult.total_return.toFixed(2)}%`);
        console.log(`    Sharpe: ${stratResult.sharpe_ratio.toFixed(2)}`);
      }
    }

  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Run if executed directly (Node.js)
if (typeof require !== 'undefined' && require.main === module) {
  main();
}

// Export for module usage
if (typeof module !== 'undefined') {
  module.exports = { QuantBacktestClient };
}
