/**
 * Anomaly Score Gauge Component
 * Visual indicator for anomaly scores with color-coded risk levels
 */

'use client'

interface AnomalyScoreGaugeProps {
  score: number // 0-1
  modelAgreement?: number // 0-1
  confidence?: number // 0-1
  size?: number
}

export function AnomalyScoreGauge({
  score,
  modelAgreement,
  confidence,
  size = 200,
}: AnomalyScoreGaugeProps) {
  // Clamp score to 0-1
  const clampedScore = Math.max(0, Math.min(1, score))

  // Calculate angle for gauge (0-180 degrees)
  const angle = clampedScore * 180

  // Determine risk level and color
  const getRiskLevel = (score: number): { level: string; color: string; textColor: string } => {
    if (score < 0.3) return { level: 'Low', color: '#10b981', textColor: 'text-green-500' }
    if (score < 0.5) return { level: 'Medium', color: '#f59e0b', textColor: 'text-amber-500' }
    if (score < 0.7) return { level: 'High', color: '#ef4444', textColor: 'text-red-500' }
    return { level: 'Critical', color: '#dc2626', textColor: 'text-red-600' }
  }

  const risk = getRiskLevel(clampedScore)

  // SVG parameters
  const centerX = size / 2
  const centerY = size / 2
  const radius = (size / 2) * 0.7
  const needleLength = radius * 0.85

  // Calculate needle endpoint
  const needleX = centerX + needleLength * Math.cos((angle - 90) * (Math.PI / 180))
  const needleY = centerY + needleLength * Math.sin((angle - 90) * (Math.PI / 180))

  // Create gradient arc path
  const createArc = (startAngle: number, endAngle: number) => {
    const start = {
      x: centerX + radius * Math.cos((startAngle - 90) * (Math.PI / 180)),
      y: centerY + radius * Math.sin((startAngle - 90) * (Math.PI / 180)),
    }
    const end = {
      x: centerX + radius * Math.cos((endAngle - 90) * (Math.PI / 180)),
      y: centerY + radius * Math.sin((endAngle - 90) * (Math.PI / 180)),
    }

    return `M ${start.x} ${start.y} A ${radius} ${radius} 0 ${endAngle - startAngle > 180 ? 1 : 0} 1 ${end.x} ${end.y}`
  }

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size * 0.7} className="overflow-visible">
        {/* Background arc */}
        <path
          d={createArc(0, 180)}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={size * 0.08}
          strokeLinecap="round"
        />

        {/* Gradient color zones */}
        <path
          d={createArc(0, 54)}
          fill="none"
          stroke="#10b981"
          strokeWidth={size * 0.08}
          strokeLinecap="round"
          opacity={0.6}
        />
        <path
          d={createArc(54, 90)}
          fill="none"
          stroke="#f59e0b"
          strokeWidth={size * 0.08}
          strokeLinecap="round"
          opacity={0.6}
        />
        <path
          d={createArc(90, 126)}
          fill="none"
          stroke="#ef4444"
          strokeWidth={size * 0.08}
          strokeLinecap="round"
          opacity={0.6}
        />
        <path
          d={createArc(126, 180)}
          fill="none"
          stroke="#dc2626"
          strokeWidth={size * 0.08}
          strokeLinecap="round"
          opacity={0.6}
        />

        {/* Active arc (score indicator) */}
        <path
          d={createArc(0, angle)}
          fill="none"
          stroke={risk.color}
          strokeWidth={size * 0.08}
          strokeLinecap="round"
        />

        {/* Needle */}
        <line
          x1={centerX}
          y1={centerY}
          x2={needleX}
          y2={needleY}
          stroke={risk.color}
          strokeWidth={3}
          strokeLinecap="round"
        />

        {/* Center circle */}
        <circle cx={centerX} cy={centerY} r={size * 0.04} fill={risk.color} />

        {/* Scale markers */}
        {[0, 0.25, 0.5, 0.75, 1].map((value, idx) => {
          const markerAngle = value * 180
          const markerStart = {
            x: centerX + (radius - size * 0.05) * Math.cos((markerAngle - 90) * (Math.PI / 180)),
            y: centerY + (radius - size * 0.05) * Math.sin((markerAngle - 90) * (Math.PI / 180)),
          }
          const markerEnd = {
            x: centerX + (radius + size * 0.02) * Math.cos((markerAngle - 90) * (Math.PI / 180)),
            y: centerY + (radius + size * 0.02) * Math.sin((markerAngle - 90) * (Math.PI / 180)),
          }

          return (
            <g key={idx}>
              <line
                x1={markerStart.x}
                y1={markerStart.y}
                x2={markerEnd.x}
                y2={markerEnd.y}
                stroke="#6b7280"
                strokeWidth={2}
              />
              <text
                x={centerX + (radius + size * 0.12) * Math.cos((markerAngle - 90) * (Math.PI / 180))}
                y={centerY + (radius + size * 0.12) * Math.sin((markerAngle - 90) * (Math.PI / 180))}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize={size * 0.08}
                className="fill-current text-muted-foreground"
              >
                {value.toFixed(1)}
              </text>
            </g>
          )
        })}

        {/* Score value */}
        <text
          x={centerX}
          y={centerY + size * 0.25}
          textAnchor="middle"
          fontSize={size * 0.15}
          fontWeight="bold"
          className={`fill-current ${risk.textColor}`}
        >
          {(clampedScore * 100).toFixed(0)}%
        </text>
      </svg>

      {/* Risk level label */}
      <div className="text-center mt-2">
        <p className={`text-lg font-bold ${risk.textColor}`}>{risk.level} Risk</p>
        {modelAgreement !== undefined && (
          <p className="text-xs text-muted-foreground mt-1">
            Model Agreement: {(modelAgreement * 100).toFixed(0)}%
          </p>
        )}
        {confidence !== undefined && (
          <p className="text-xs text-muted-foreground">
            Confidence: {(confidence * 100).toFixed(0)}%
          </p>
        )}
      </div>
    </div>
  )
}
