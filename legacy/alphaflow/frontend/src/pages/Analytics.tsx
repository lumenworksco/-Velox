import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { format, subDays } from 'date-fns'
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  Award,
  DollarSign,
  BarChart3,
  Calendar,
  AlertCircle,
  CheckCircle,
} from 'lucide-react'
import {
  getPerformanceMetrics,
  getEquityCurve,
  getTradeHistory,
  getMonthlyReturns,
  getRiskMetrics,
} from '../api/analytics'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

export default function Analytics() {
  const [timeRange, setTimeRange] = useState<'1M' | '3M' | '6M' | '1Y' | 'ALL'>('3M')

  const getDateRange = () => {
    const end = new Date()
    let start: Date
    switch (timeRange) {
      case '1M':
        start = subDays(end, 30)
        break
      case '3M':
        start = subDays(end, 90)
        break
      case '6M':
        start = subDays(end, 180)
        break
      case '1Y':
        start = subDays(end, 365)
        break
      case 'ALL':
        return { startDate: undefined, endDate: undefined }
    }
    return {
      startDate: format(start, 'yyyy-MM-dd'),
      endDate: format(end, 'yyyy-MM-dd'),
    }
  }

  const { startDate, endDate } = getDateRange()

  // Fetch performance metrics
  const { data: metrics } = useQuery({
    queryKey: ['performance-metrics', startDate, endDate],
    queryFn: () => getPerformanceMetrics(startDate, endDate),
  })

  // Fetch equity curve
  const { data: equityCurve } = useQuery({
    queryKey: ['equity-curve', startDate, endDate],
    queryFn: () => getEquityCurve(startDate, endDate),
  })

  // Fetch trade history
  const { data: tradesData } = useQuery({
    queryKey: ['trade-history'],
    queryFn: () => getTradeHistory(50, 0),
  })

  // Fetch monthly returns
  const { data: monthlyReturns } = useQuery({
    queryKey: ['monthly-returns'],
    queryFn: () => getMonthlyReturns(),
  })

  // Fetch risk metrics
  const { data: riskMetrics } = useQuery({
    queryKey: ['risk-metrics'],
    queryFn: () => getRiskMetrics(),
  })

  // Transform equity curve data for charts
  const equityChartData = equityCurve?.map((point) => ({
    date: format(new Date(point.timestamp), 'MMM d'),
    equity: point.equity,
    dailyReturn: point.daily_return,
  })) || []

  // Calculate drawdown data
  const drawdownData = equityCurve?.map((point, idx, arr) => {
    const maxEquity = Math.max(...arr.slice(0, idx + 1).map(p => p.equity))
    const drawdown = ((point.equity - maxEquity) / maxEquity) * 100
    return {
      date: format(new Date(point.timestamp), 'MMM d'),
      drawdown,
    }
  }) || []

  // Transform monthly returns for heatmap
  const monthlyReturnsData = monthlyReturns ? Object.entries(monthlyReturns).flatMap(([year, months]) =>
    Object.entries(months).map(([month, return_pct]) => ({
      year,
      month,
      return: return_pct,
    }))
  ) : []

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Performance Analytics</h1>
          <p className="text-text-secondary mt-1">Comprehensive analysis of your trading performance</p>
        </div>

        {/* Time Range Selector */}
        <div className="flex items-center space-x-2 bg-primary-surface rounded-lg border border-primary-border p-1">
          {(['1M', '3M', '6M', '1Y', 'ALL'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                timeRange === range
                  ? 'bg-accent-blue text-white'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Performance Metrics Grid */}
      {metrics && (
        <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          {/* Total Return */}
          <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp className="w-4 h-4 text-text-secondary" />
              <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                Total Return
              </span>
            </div>
            <div
              className={`text-2xl font-bold tabular-nums ${
                metrics.total_return >= 0 ? 'text-semantic-positive' : 'text-semantic-negative'
              }`}
            >
              {metrics.total_return >= 0 ? '+' : ''}
              {metrics.total_return.toFixed(2)}%
            </div>
          </div>

          {/* Sharpe Ratio */}
          <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Activity className="w-4 h-4 text-text-secondary" />
              <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                Sharpe Ratio
              </span>
            </div>
            <div className="text-2xl font-bold text-text-primary tabular-nums">
              {metrics.sharpe_ratio.toFixed(2)}
            </div>
          </div>

          {/* Max Drawdown */}
          <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingDown className="w-4 h-4 text-text-secondary" />
              <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                Max Drawdown
              </span>
            </div>
            <div className="text-2xl font-bold text-semantic-negative tabular-nums">
              {metrics.max_drawdown.toFixed(2)}%
            </div>
          </div>

          {/* Win Rate */}
          <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Award className="w-4 h-4 text-text-secondary" />
              <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                Win Rate
              </span>
            </div>
            <div className="text-2xl font-bold text-text-primary tabular-nums">
              {metrics.win_rate.toFixed(1)}%
            </div>
          </div>

          {/* Profit Factor */}
          <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Target className="w-4 h-4 text-text-secondary" />
              <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                Profit Factor
              </span>
            </div>
            <div className="text-2xl font-bold text-text-primary tabular-nums">
              {metrics.profit_factor.toFixed(2)}
            </div>
          </div>

          {/* Total Trades */}
          <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
            <div className="flex items-center space-x-2 mb-2">
              <BarChart3 className="w-4 h-4 text-text-secondary" />
              <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                Total Trades
              </span>
            </div>
            <div className="text-2xl font-bold text-text-primary tabular-nums">
              {metrics.total_trades}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Equity Curve */}
        <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">Equity Curve</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={equityChartData}>
              <defs>
                <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2962FF" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#2962FF" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A2E39" />
              <XAxis dataKey="date" stroke="#848E9C" style={{ fontSize: '12px' }} />
              <YAxis
                stroke="#848E9C"
                style={{ fontSize: '12px' }}
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#131722',
                  border: '1px solid #2A2E39',
                  borderRadius: '8px',
                }}
                labelStyle={{ color: '#E0E3EB' }}
                formatter={(value: number) => [
                  `$${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}`,
                  'Equity',
                ]}
              />
              <Area
                type="monotone"
                dataKey="equity"
                stroke="#2962FF"
                strokeWidth={2}
                fill="url(#equityGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Drawdown Chart */}
        <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">Drawdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={drawdownData}>
              <defs>
                <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#EF5350" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#EF5350" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A2E39" />
              <XAxis dataKey="date" stroke="#848E9C" style={{ fontSize: '12px' }} />
              <YAxis
                stroke="#848E9C"
                style={{ fontSize: '12px' }}
                tickFormatter={(value) => `${value.toFixed(0)}%`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#131722',
                  border: '1px solid #2A2E39',
                  borderRadius: '8px',
                }}
                labelStyle={{ color: '#E0E3EB' }}
                formatter={(value: number) => [`${value.toFixed(2)}%`, 'Drawdown']}
              />
              <ReferenceLine y={0} stroke="#848E9C" strokeDasharray="3 3" />
              <Area
                type="monotone"
                dataKey="drawdown"
                stroke="#EF5350"
                strokeWidth={2}
                fill="url(#drawdownGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Advanced Metrics */}
      {metrics && riskMetrics && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Risk-Adjusted Returns */}
          <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
            <h3 className="text-lg font-semibold text-text-primary mb-4">Risk-Adjusted Returns</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-text-secondary">Sortino Ratio</span>
                <span className="text-text-primary font-semibold tabular-nums">
                  {metrics.sortino_ratio.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Calmar Ratio</span>
                <span className="text-text-primary font-semibold tabular-nums">
                  {metrics.calmar_ratio.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Recovery Factor</span>
                <span className="text-text-primary font-semibold tabular-nums">
                  {metrics.recovery_factor.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Alpha</span>
                <span className="text-text-primary font-semibold tabular-nums">
                  {riskMetrics.alpha.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Beta</span>
                <span className="text-text-primary font-semibold tabular-nums">
                  {riskMetrics.beta.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Trade Statistics */}
          <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
            <h3 className="text-lg font-semibold text-text-primary mb-4">Trade Statistics</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-text-secondary">Avg Trade Return</span>
                <span
                  className={`font-semibold tabular-nums ${
                    metrics.avg_trade_return >= 0 ? 'text-semantic-positive' : 'text-semantic-negative'
                  }`}
                >
                  {metrics.avg_trade_return >= 0 ? '+' : ''}
                  {metrics.avg_trade_return.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Avg Win</span>
                <span className="text-semantic-positive font-semibold tabular-nums">
                  +{metrics.avg_win.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Avg Loss</span>
                <span className="text-semantic-negative font-semibold tabular-nums">
                  {metrics.avg_loss.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Best Trade</span>
                <span className="text-semantic-positive font-semibold tabular-nums">
                  +{metrics.best_trade.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Worst Trade</span>
                <span className="text-semantic-negative font-semibold tabular-nums">
                  {metrics.worst_trade.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>

          {/* Risk Metrics */}
          <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
            <h3 className="text-lg font-semibold text-text-primary mb-4">Risk Metrics</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-text-secondary">VaR (95%)</span>
                <span className="text-semantic-negative font-semibold tabular-nums">
                  {riskMetrics.var_95.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">VaR (99%)</span>
                <span className="text-semantic-negative font-semibold tabular-nums">
                  {riskMetrics.var_99.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">CVaR (95%)</span>
                <span className="text-semantic-negative font-semibold tabular-nums">
                  {riskMetrics.cvar_95.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Volatility</span>
                <span className="text-text-primary font-semibold tabular-nums">
                  {riskMetrics.volatility.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Correlation (SPY)</span>
                <span className="text-text-primary font-semibold tabular-nums">
                  {riskMetrics.correlation_to_spy.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Trade History */}
      {tradesData && tradesData.trades.length > 0 && (
        <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">Recent Trades</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-primary-border text-left">
                  <th className="pb-3 text-xs uppercase tracking-wider text-text-secondary font-semibold">
                    Symbol
                  </th>
                  <th className="pb-3 text-xs uppercase tracking-wider text-text-secondary font-semibold">
                    Side
                  </th>
                  <th className="pb-3 text-xs uppercase tracking-wider text-text-secondary font-semibold">
                    Qty
                  </th>
                  <th className="pb-3 text-xs uppercase tracking-wider text-text-secondary font-semibold">
                    Entry
                  </th>
                  <th className="pb-3 text-xs uppercase tracking-wider text-text-secondary font-semibold">
                    Exit
                  </th>
                  <th className="pb-3 text-xs uppercase tracking-wider text-text-secondary font-semibold">
                    Duration
                  </th>
                  <th className="pb-3 text-xs uppercase tracking-wider text-text-secondary font-semibold">
                    P&L
                  </th>
                  <th className="pb-3 text-xs uppercase tracking-wider text-text-secondary font-semibold">
                    Return
                  </th>
                  <th className="pb-3 text-xs uppercase tracking-wider text-text-secondary font-semibold">
                    Strategy
                  </th>
                </tr>
              </thead>
              <tbody>
                {tradesData.trades.slice(0, 20).map((trade) => (
                  <tr
                    key={trade.trade_id}
                    className="border-b border-primary-border hover:bg-primary-hover transition-colors"
                  >
                    <td className="py-3 text-text-primary font-medium">{trade.symbol}</td>
                    <td className="py-3">
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${
                          trade.side === 'buy'
                            ? 'bg-semantic-positive/20 text-semantic-positive'
                            : 'bg-semantic-negative/20 text-semantic-negative'
                        }`}
                      >
                        {trade.side.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 text-text-primary tabular-nums">{trade.quantity}</td>
                    <td className="py-3 text-text-primary tabular-nums">
                      ${trade.entry_price.toFixed(2)}
                    </td>
                    <td className="py-3 text-text-primary tabular-nums">
                      ${trade.exit_price.toFixed(2)}
                    </td>
                    <td className="py-3 text-text-secondary tabular-nums">
                      {trade.duration_hours.toFixed(1)}h
                    </td>
                    <td
                      className={`py-3 font-semibold tabular-nums ${
                        trade.pnl >= 0 ? 'text-semantic-positive' : 'text-semantic-negative'
                      }`}
                    >
                      {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                    </td>
                    <td
                      className={`py-3 font-semibold tabular-nums ${
                        trade.pnl_percent >= 0 ? 'text-semantic-positive' : 'text-semantic-negative'
                      }`}
                    >
                      {trade.pnl_percent >= 0 ? '+' : ''}
                      {trade.pnl_percent.toFixed(2)}%
                    </td>
                    <td className="py-3 text-text-secondary text-sm">{trade.strategy}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
