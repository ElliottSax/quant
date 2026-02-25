/**
 * Time Series Chart Component
 * Visualizes trade frequency and patterns over time with forecast overlay
 */

'use client'

import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

interface TimeSeriesDataPoint {
  date: string
  value: number
  forecast?: number
  upper_bound?: number
  lower_bound?: number
}

interface TimeSeriesChartProps {
  data: TimeSeriesDataPoint[]
  title?: string
  dataKey?: string
  forecastKey?: string
  showForecast?: boolean
  height?: number
}

export function TimeSeriesChart({
  data,
  title,
  dataKey = 'value',
  forecastKey = 'forecast',
  showForecast = false,
  height = 300,
}: TimeSeriesChartProps) {
  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#82ca9d" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => {
              const date = new Date(value)
              return `${date.getMonth() + 1}/${date.getDate()}`
            }}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
            }}
            labelFormatter={(value) => new Date(value).toLocaleDateString()}
          />
          <Legend />

          {/* Historical data */}
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke="#8884d8"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorValue)"
            name="Trade Frequency"
          />

          {/* Forecast data */}
          {showForecast && (
            <>
              <Area
                type="monotone"
                dataKey={forecastKey}
                stroke="#82ca9d"
                strokeWidth={2}
                strokeDasharray="5 5"
                fillOpacity={1}
                fill="url(#colorForecast)"
                name="Forecast"
              />
              {data.some(d => d.upper_bound) && (
                <Line
                  type="monotone"
                  dataKey="upper_bound"
                  stroke="#82ca9d"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                  dot={false}
                  name="Upper Bound"
                />
              )}
              {data.some(d => d.lower_bound) && (
                <Line
                  type="monotone"
                  dataKey="lower_bound"
                  stroke="#82ca9d"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                  dot={false}
                  name="Lower Bound"
                />
              )}
            </>
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
