import React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { OUTPUT_CONFIG, formatValue, getChangeColor } from '../utils/constants'

export default function ResultCard({ metric, value, baseline = null }) {
  const config = OUTPUT_CONFIG[metric]
  if (!config) return null

  const change = baseline !== null ? value - baseline : null
  const changePercent = baseline !== null && baseline !== 0
    ? ((value - baseline) / Math.abs(baseline)) * 100
    : null

  const isPositive = value > 0 || (metric === 'employment_rate' && value > 90)
  const colorClass = getChangeColor(
    change !== null ? change : value,
    config.goodDirection
  )

  return (
    <div className="glass-card-hover p-5 group">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">
          {config.label}
        </span>
        <div className={`p-1.5 rounded-lg ${
          isPositive ? 'bg-emerald-500/10' : 'bg-red-500/10'
        }`}>
          {change > 0 ? (
            <TrendingUp className={`w-3.5 h-3.5 ${isPositive ? 'text-emerald-400' : 'text-red-400'}`} />
          ) : change < 0 ? (
            <TrendingDown className={`w-3.5 h-3.5 ${isPositive ? 'text-emerald-400' : 'text-red-400'}`} />
          ) : (
            <Minus className="w-3.5 h-3.5 text-gray-400" />
          )}
        </div>
      </div>

      <div className="mb-2">
        <span 
          className="text-3xl font-bold font-display transition-colors duration-300"
          style={{ color: config.color }}
        >
          {formatValue(value, '')}
        </span>
        <span className="text-sm text-gray-400 ml-1">{config.unit}</span>
      </div>

      {changePercent !== null && (
        <div className={`flex items-center gap-1 text-xs font-medium ${colorClass}`}>
          {change > 0 ? '+' : ''}{changePercent.toFixed(1)}% from baseline
        </div>
      )}
    </div>
  )
}
