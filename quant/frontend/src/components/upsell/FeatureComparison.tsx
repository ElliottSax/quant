'use client'

import { Check, X } from 'lucide-react'

interface Feature {
  name: string
  free: boolean | string
  premium: boolean | string
  enterprise: boolean | string
}

interface FeatureComparisonProps {
  currentTier?: 'free' | 'premium' | 'enterprise'
}

const features: Feature[] = [
  {
    name: 'Monthly Backtests',
    free: '5',
    premium: '50',
    enterprise: 'Unlimited',
  },
  {
    name: 'Strategy Templates',
    free: 'Basic (3)',
    premium: 'All (10+)',
    enterprise: 'All + Custom',
  },
  {
    name: 'Historical Data Lookback',
    free: '1 year',
    premium: '10 years',
    enterprise: 'Unlimited',
  },
  {
    name: 'Portfolio Backtesting',
    free: false,
    premium: true,
    enterprise: true,
  },
  {
    name: 'Advanced Optimization',
    free: false,
    premium: true,
    enterprise: true,
  },
  {
    name: 'Email Alerts',
    free: false,
    premium: true,
    enterprise: true,
  },
  {
    name: 'Saved Strategies',
    free: '5',
    premium: 'Unlimited',
    enterprise: 'Unlimited',
  },
  {
    name: 'API Access',
    free: false,
    premium: false,
    enterprise: true,
  },
  {
    name: 'White-Label Options',
    free: false,
    premium: false,
    enterprise: true,
  },
  {
    name: 'Priority Support',
    free: false,
    premium: true,
    enterprise: true,
  },
]

export function FeatureComparison({
  currentTier = 'free',
}: FeatureComparisonProps) {
  const FeatureValue = ({ value }: { value: boolean | string }) => {
    if (typeof value === 'boolean') {
      return value ? (
        <Check className="w-5 h-5 text-green-400" />
      ) : (
        <X className="w-5 h-5 text-slate-500" />
      )
    }
    return <span className="text-sm font-medium">{value}</span>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700">
            <th className="text-left py-4 px-4 font-semibold text-white">Feature</th>
            <th className="text-center py-4 px-4 font-semibold text-white">
              Free
              {currentTier === 'free' && (
                <div className="text-xs text-blue-400 font-normal mt-1">Current</div>
              )}
            </th>
            <th className="text-center py-4 px-4 font-semibold text-white">
              Premium
              {currentTier === 'premium' && (
                <div className="text-xs text-blue-400 font-normal mt-1">Current</div>
              )}
            </th>
            <th className="text-center py-4 px-4 font-semibold text-white">
              Enterprise
              {currentTier === 'enterprise' && (
                <div className="text-xs text-blue-400 font-normal mt-1">Current</div>
              )}
            </th>
          </tr>
        </thead>
        <tbody>
          {features.map((feature, idx) => (
            <tr
              key={idx}
              className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors"
            >
              <td className="py-4 px-4 text-left text-slate-300">{feature.name}</td>
              <td className="py-4 px-4 text-center">
                <FeatureValue value={feature.free} />
              </td>
              <td className="py-4 px-4 text-center">
                <FeatureValue value={feature.premium} />
              </td>
              <td className="py-4 px-4 text-center">
                <FeatureValue value={feature.enterprise} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
