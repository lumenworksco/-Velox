import { TrendingUp, TrendingDown } from 'lucide-react'

interface MetricCardProps {
  label: string
  value: string
  change?: number
}

export default function MetricCard({ label, value, change }: MetricCardProps) {
  const isPositive = change !== undefined && change >= 0
  const showChange = change !== undefined && change !== 0

  return (
    <div className="bg-primary-surface rounded-lg border border-primary-border p-6 hover:border-accent-blue/50 transition-colors fade-in">
      {/* Label */}
      <div className="text-xs uppercase tracking-wider text-text-secondary font-semibold mb-3">
        {label}
      </div>

      {/* Value */}
      <div className="text-3xl font-bold text-text-primary tabular-nums mb-2">
        {value}
      </div>

      {/* Change Indicator */}
      {showChange && (
        <div className={`flex items-center text-sm font-medium ${
          isPositive ? 'text-semantic-positive' : 'text-semantic-negative'
        }`}>
          {isPositive ? (
            <TrendingUp className="w-4 h-4 mr-1" />
          ) : (
            <TrendingDown className="w-4 h-4 mr-1" />
          )}
          <span className="tabular-nums">
            {isPositive ? '+' : ''}{change.toFixed(2)}%
          </span>
        </div>
      )}
    </div>
  )
}
