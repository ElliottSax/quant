/**
 * Experiment Results Component
 * Shows recent model experiments and their performance
 */

'use client'

interface Experiment {
  id: string
  experiment_date: string
  model_name: string
  deployment_ready: boolean
  validation_metrics?: {
    accuracy?: number
    precision?: number
    recall?: number
  }
}

interface ExperimentResultsProps {
  experiments?: Experiment[]
}

export function ExperimentResults({ experiments }: ExperimentResultsProps) {
  if (!experiments || experiments.length === 0) {
    return (
      <div className="text-sm text-muted-foreground text-center py-8">
        No recent experiments
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {experiments.slice(0, 5).map((exp) => (
        <div
          key={exp.id}
          className="p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
        >
          <div className="flex items-start justify-between mb-2">
            <div className="font-medium text-sm">{exp.model_name}</div>
            {exp.deployment_ready && (
              <span className="px-2 py-1 text-xs font-medium bg-green-500/10 text-green-600 rounded-full">
                Ready
              </span>
            )}
          </div>
          {exp.validation_metrics && (
            <div className="text-xs text-muted-foreground space-y-1">
              {exp.validation_metrics.accuracy && (
                <div className="flex justify-between">
                  <span>Accuracy:</span>
                  <span className="font-medium">
                    {(exp.validation_metrics.accuracy * 100).toFixed(1)}%
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
