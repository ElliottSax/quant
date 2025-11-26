/**
 * Anomaly Alerts Component - Shows critical anomalies requiring investigation
 */

import { formatDistanceToNow } from 'date-fns'
import Link from 'next/link'

interface Anomaly {
  id: string
  detection_date: string
  politician_id: string
  politician_name: string
  anomaly_type: string
  severity: number
  description: string
  evidence: Record<string, any>
  investigated: boolean
}

interface AnomalyAlertsProps {
  anomalies: Anomaly[]
}

export function AnomalyAlerts({ anomalies }: AnomalyAlertsProps) {
  return (
    <div className="space-y-3">
      {anomalies.map((anomaly) => (
        <AnomalyCard key={anomaly.id} anomaly={anomaly} />
      ))}
    </div>
  )
}

function AnomalyCard({ anomaly }: { anomaly: Anomaly }) {
  const severityConfig = getSeverityConfig(anomaly.severity)

  return (
    <div
      className={`
        border-l-4 p-4 rounded-lg bg-card
        ${severityConfig.borderColor}
      `}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Header */}
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xl">{severityConfig.icon}</span>
            <div>
              <h4 className="font-semibold">{getAnomalyTitle(anomaly.anomaly_type)}</h4>
              <Link
                href={`/politicians/${anomaly.politician_id}`}
                className="text-sm text-primary hover:underline"
              >
                {anomaly.politician_name}
              </Link>
            </div>
          </div>

          {/* Description */}
          <p className="text-sm text-muted-foreground mb-3">{anomaly.description}</p>

          {/* Evidence Summary */}
          <div className="space-y-2">
            {Object.entries(anomaly.evidence).slice(0, 3).map(([key, value]) => (
              <div key={key} className="flex items-center gap-2 text-xs">
                <span className="text-muted-foreground">{formatEvidenceKey(key)}:</span>
                <span className="font-medium">{formatEvidenceValue(value)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Severity Badge */}
        <div className="text-right">
          <div className={`
            px-3 py-1 rounded-full text-xs font-semibold
            ${severityConfig.bgColor} ${severityConfig.textColor}
          `}>
            {(anomaly.severity * 100).toFixed(0)}% Severity
          </div>
          <div className="text-xs text-muted-foreground mt-2">
            {formatDistanceToNow(new Date(anomaly.detection_date), { addSuffix: true })}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3 mt-4 pt-3 border-t border-border">
        <Link
          href={`/anomalies/${anomaly.id}`}
          className="text-sm font-medium text-primary hover:underline"
        >
          Investigate →
        </Link>
        <Link
          href={`/politicians/${anomaly.politician_id}`}
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          View Trades
        </Link>
      </div>
    </div>
  )
}

function getSeverityConfig(severity: number) {
  if (severity >= 0.9) {
    return {
      icon: '🚨',
      borderColor: 'border-l-red-500',
      bgColor: 'bg-red-500',
      textColor: 'text-white',
    }
  } else if (severity >= 0.8) {
    return {
      icon: '⚠️',
      borderColor: 'border-l-amber-500',
      bgColor: 'bg-amber-500',
      textColor: 'text-white',
    }
  } else {
    return {
      icon: '⚡',
      borderColor: 'border-l-blue-500',
      bgColor: 'bg-blue-500',
      textColor: 'text-white',
    }
  }
}

function getAnomalyTitle(type: string): string {
  const titles = {
    statistical_outlier: 'Statistical Outlier Detected',
    model_disagreement: 'Model Disagreement',
    off_cycle: 'Off-Cycle Trading',
    regime_change: 'Sudden Regime Change',
    network_anomaly: 'Network Coordination Anomaly',
    volume_spike: 'Unusual Volume Spike',
    no_precedent: 'No Historical Precedent',
  }
  return titles[type] || type.replace('_', ' ')
}

function formatEvidenceKey(key: string): string {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function formatEvidenceValue(value: any): string {
  if (typeof value === 'number') {
    return value.toFixed(2)
  }
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No'
  }
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return String(value)
}
