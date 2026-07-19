/**
 * Strategy templates + indicator/operator vocabularies for the backtesting builder.
 * Restored module (referenced by src/app/backtesting/* and consumers).
 */

export type StrategyCategory = 'trend' | 'mean_reversion' | 'momentum' | 'breakout';
export type StrategyTier = 'free' | 'pro';

export interface StrategyParameter {
  name: string;
  label?: string;
  default: number;
  min?: number;
  max?: number;
}

export interface StrategyDefinition {
  id: string;
  name: string;
  description: string;
  category: StrategyCategory;
  tier: StrategyTier;
  parameters: StrategyParameter[];
}

export interface Indicator {
  id: string;
  name: string;
  type?: string;
}

export type ConditionOperator = 'gt' | 'lt' | 'gte' | 'lte' | 'cross_above' | 'cross_below';

export interface ConditionOperatorDef {
  operator: ConditionOperator;
  label: string;
}

export const INDICATORS: Indicator[] = [
  { id: 'price', name: 'Price', type: 'price' },
  { id: 'sma', name: 'Simple Moving Average', type: 'overlay' },
  { id: 'ema', name: 'Exponential Moving Average', type: 'overlay' },
  { id: 'rsi', name: 'RSI', type: 'oscillator' },
  { id: 'macd', name: 'MACD', type: 'oscillator' },
  { id: 'bbands', name: 'Bollinger Bands', type: 'overlay' },
  { id: 'atr', name: 'Average True Range', type: 'volatility' },
];

export const CONDITION_OPERATORS: ConditionOperatorDef[] = [
  { operator: 'gt', label: 'is greater than' },
  { operator: 'lt', label: 'is less than' },
  { operator: 'gte', label: 'is greater than or equal to' },
  { operator: 'lte', label: 'is less than or equal to' },
  { operator: 'cross_above', label: 'crosses above' },
  { operator: 'cross_below', label: 'crosses below' },
];

export const STRATEGIES: StrategyDefinition[] = [
  {
    id: 'sma-crossover',
    name: 'SMA Crossover',
    description: 'Buy when a fast moving average crosses above a slow one; sell on the reverse cross.',
    category: 'trend',
    tier: 'free',
    parameters: [
      { name: 'fast', label: 'Fast period', default: 20, min: 2, max: 200 },
      { name: 'slow', label: 'Slow period', default: 50, min: 5, max: 400 },
    ],
  },
  {
    id: 'rsi-mean-reversion',
    name: 'RSI Mean Reversion',
    description: 'Buy when RSI is oversold and sell when it returns to overbought territory.',
    category: 'mean_reversion',
    tier: 'free',
    parameters: [
      { name: 'period', label: 'RSI period', default: 14, min: 2, max: 50 },
      { name: 'oversold', label: 'Oversold level', default: 30, min: 5, max: 45 },
      { name: 'overbought', label: 'Overbought level', default: 70, min: 55, max: 95 },
    ],
  },
  {
    id: 'momentum-breakout',
    name: 'Momentum Breakout',
    description: 'Enter on a breakout above the recent high to ride momentum.',
    category: 'momentum',
    tier: 'free',
    parameters: [
      { name: 'lookback', label: 'Lookback period', default: 20, min: 5, max: 120 },
    ],
  },
];

export function getStrategyById(id: string): StrategyDefinition | undefined {
  return STRATEGIES.find((s) => s.id === id);
}
