/**
 * Discovery Statistics Component
 * Shows overview stats for discoveries
 */

'use client'

interface DiscoveryStatsProps {
  totalDiscoveries: number
  criticalAnomalies: number
  newExperiments: number
}

export function DiscoveryStats({
  totalDiscoveries,
  criticalAnomalies,
  newExperiments,
}: DiscoveryStatsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <StatCard
        title="Total Discoveries"
        value={totalDiscoveries}
        subtitle="Patterns found"
        trend="+12%"
      />
      <StatCard
        title="Critical Anomalies"
        value={criticalAnomalies}
        subtitle="Require investigation"
        trend="⚠️"
        danger
      />
      <StatCard
        title="New Models"
        value={newExperiments}
        subtitle="Ready for deployment"
        trend="✅"
      />
    </div>
  )
}

interface StatCardProps {
  title: string
  value: number
  subtitle: string
  trend?: string
  danger?: boolean
}

function StatCard({ title, value, subtitle, trend, danger }: StatCardProps) {
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <p className="text-sm text-muted-foreground mb-2">{title}</p>
      <p className={`text-3xl font-bold mb-1 ${danger ? 'text-red-500' : ''}`}>
        {value.toLocaleString()}
      </p>
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">{subtitle}</p>
        {trend && <span className="text-xs font-medium">{trend}</span>}
      </div>
    </div>
  )
}
