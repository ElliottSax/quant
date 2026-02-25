"use client";

import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from 'recharts';

interface EfficientFrontierProps {
  returns: number[];
  volatilities: number[];
  sharpeRatios: number[];
}

export function EfficientFrontierChart({ returns, volatilities, sharpeRatios }: EfficientFrontierProps) {
  const data = returns.map((ret, idx) => ({
    volatility: volatilities[idx] * 100,
    return: ret * 100,
    sharpe: sharpeRatios[idx]
  }));

  // Find max Sharpe ratio point
  const maxSharpeIdx = sharpeRatios.indexOf(Math.max(...sharpeRatios));
  const optimalPoint = [{
    volatility: volatilities[maxSharpeIdx] * 100,
    return: returns[maxSharpeIdx] * 100,
    sharpe: sharpeRatios[maxSharpeIdx]
  }];

  return (
    <div className="w-full h-96 bg-white dark:bg-slate-800 rounded-lg p-4 shadow-lg">
      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
        Efficient Frontier
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis
            type="number"
            dataKey="volatility"
            name="Volatility"
            unit="%"
            stroke="#888"
            tick={{ fill: '#888' }}
            label={{ value: 'Volatility (%)', position: 'insideBottom', offset: -5, fill: '#888' }}
          />
          <YAxis
            type="number"
            dataKey="return"
            name="Return"
            unit="%"
            stroke="#888"
            tick={{ fill: '#888' }}
            label={{ value: 'Expected Return (%)', angle: -90, position: 'insideLeft', fill: '#888' }}
          />
          <ZAxis range={[50, 200]} />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              borderRadius: '8px'
            }}
            formatter={(value: number) => value.toFixed(2)}
          />
          <Scatter
            name="Efficient Frontier"
            data={data}
            fill="#3b82f6"
            opacity={0.6}
          />
          <Scatter
            name="Optimal (Max Sharpe)"
            data={optimalPoint}
            fill="#10b981"
            shape="star"
          />
        </ScatterChart>
      </ResponsiveContainer>
      <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
        <p>🟢 Green star = Maximum Sharpe Ratio portfolio</p>
        <p>🔵 Blue dots = Other efficient portfolios</p>
      </div>
    </div>
  );
}
