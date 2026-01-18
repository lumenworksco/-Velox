import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import { Play, TrendingUp, Activity, Target, Award, Clock } from 'lucide-react'
import { runBacktest, getBacktestStatus, getBacktestResults } from '../api/backtest'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'

const STRATEGIES = [
  { id: 'Technical Momentum', name: 'Technical Momentum', description: 'Trend following with RSI and MACD' },
  { id: 'Mean Reversion', name: 'Mean Reversion', description: 'Buy oversold, sell overbought' },
  { id: 'Breakout Strategy', name: 'Breakout Strategy', description: 'Trade Bollinger Band breakouts' },
  { id: 'ML Momentum', name: 'ML Momentum', description: 'Machine learning predictions' },
  { id: 'Multi-Timeframe', name: 'Multi-Timeframe Trend', description: 'Analyze across multiple timeframes' },
]

export default function Backtest() {
  const [symbols, setSymbols] = useState('AAPL\nMSFT\nGOOGL')
  const [strategy, setStrategy] = useState('Technical Momentum')
  const [startDate, setStartDate] = useState(
    format(new Date(Date.now() - 90 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd')
  )
  const [endDate, setEndDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [initialCapital, setInitialCapital] = useState('100000')
  const [commission, setCommission] = useState('0.001')
  const [backtestId, setBacktestId] = useState<string | null>(null)

  // Run backtest mutation
  const runBacktestMutation = useMutation({
    mutationFn: runBacktest,
    onSuccess: (data) => {
      setBacktestId(data.backtest_id)
    },
  })

  // Poll backtest status
  const { data: status } = useQuery({
    queryKey: ['backtest-status', backtestId],
    queryFn: () => getBacktestStatus(backtestId!),
    enabled: !!backtestId,
    refetchInterval: (data) => {
      return data?.status === 'running' ? 1000 : false
    },
  })

  // Get results when complete
  const { data: results } = useQuery({
    queryKey: ['backtest-results', backtestId],
    queryFn: () => getBacktestResults(backtestId!),
    enabled: !!backtestId && status?.status === 'completed',
  })

  const handleRunBacktest = () => {
    const symbolList = symbols.split('\n').map(s => s.trim()).filter(s => s.length > 0)

    runBacktestMutation.mutate({
      symbols: symbolList,
      strategy,
      start_date: startDate,
      end_date: endDate,
      initial_capital: parseFloat(initialCapital),
      commission: parseFloat(commission),
    })
  }

  const isRunning = status?.status === 'running'
  const isComplete = status?.status === 'completed'

  // Mock equity curve data for visualization
  const equityCurveData = results ? Array.from({ length: 30 }, (_, i) => ({
    day: i + 1,
    equity: 100000 * (1 + (results.total_return / 100) * (i / 30) + (Math.random() - 0.5) * 0.02)
  })) : []

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Strategy Backtesting</h1>
          <p className="text-text-secondary mt-1">Test your trading strategies on historical data</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">Configuration</h3>

          <div className="space-y-4">
            {/* Strategy Selection */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Strategy
              </label>
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-2 px-3 text-text-primary focus:outline-none focus:border-accent-blue"
              >
                {STRATEGIES.map((strat) => (
                  <option key={strat.id} value={strat.id}>
                    {strat.name}
                  </option>
                ))}
              </select>
              <p className="text-xs text-text-tertiary mt-1">
                {STRATEGIES.find(s => s.id === strategy)?.description}
              </p>
            </div>

            {/* Symbols */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Symbols (one per line)
              </label>
              <textarea
                value={symbols}
                onChange={(e) => setSymbols(e.target.value)}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-2 px-3 text-text-primary focus:outline-none focus:border-accent-blue font-mono text-sm"
                rows={4}
                placeholder="AAPL&#10;MSFT&#10;GOOGL"
              />
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full bg-primary-elevated border border-primary-border rounded-lg py-2 px-3 text-text-primary focus:outline-none focus:border-accent-blue"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full bg-primary-elevated border border-primary-border rounded-lg py-2 px-3 text-text-primary focus:outline-none focus:border-accent-blue"
                />
              </div>
            </div>

            {/* Parameters */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Initial Capital
              </label>
              <input
                type="number"
                value={initialCapital}
                onChange={(e) => setInitialCapital(e.target.value)}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-2 px-3 text-text-primary focus:outline-none focus:border-accent-blue"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Commission (%)
              </label>
              <input
                type="number"
                value={commission}
                onChange={(e) => setCommission(e.target.value)}
                step="0.0001"
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-2 px-3 text-text-primary focus:outline-none focus:border-accent-blue"
              />
            </div>

            {/* Run Button */}
            <button
              onClick={handleRunBacktest}
              disabled={isRunning}
              className="w-full bg-accent-blue hover:bg-accent-blue-hover disabled:bg-primary-elevated disabled:text-text-tertiary text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center space-x-2"
            >
              <Play className="w-5 h-5" />
              <span>{isRunning ? 'Running...' : 'Run Backtest'}</span>
            </button>

            {/* Progress */}
            {isRunning && status && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">{status.message}</span>
                  <span className="text-text-primary font-semibold">{status.progress}%</span>
                </div>
                <div className="w-full bg-primary-elevated rounded-full h-2">
                  <div
                    className="bg-accent-blue h-2 rounded-full transition-all duration-300"
                    style={{ width: `${status.progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-6">
          {!isComplete ? (
            <div className="bg-primary-surface rounded-lg border border-primary-border p-12 flex flex-col items-center justify-center text-center">
              <Activity className="w-16 h-16 text-text-tertiary mb-4" />
              <h3 className="text-xl font-semibold text-text-primary mb-2">
                {isRunning ? 'Backtest Running...' : 'No Results Yet'}
              </h3>
              <p className="text-text-secondary">
                {isRunning
                  ? 'Testing your strategy on historical data'
                  : 'Configure your backtest and click Run to see results'}
              </p>
            </div>
          ) : results && (
            <>
              {/* Performance Metrics */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-text-secondary" />
                    <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                      Total Return
                    </span>
                  </div>
                  <div className={`text-2xl font-bold tabular-nums ${
                    results.total_return >= 0 ? 'text-semantic-positive' : 'text-semantic-negative'
                  }`}>
                    {results.total_return >= 0 ? '+' : ''}{results.total_return.toFixed(2)}%
                  </div>
                </div>

                <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Activity className="w-4 h-4 text-text-secondary" />
                    <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                      Sharpe Ratio
                    </span>
                  </div>
                  <div className="text-2xl font-bold text-text-primary tabular-nums">
                    {results.sharpe_ratio.toFixed(2)}
                  </div>
                </div>

                <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Target className="w-4 h-4 text-text-secondary" />
                    <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                      Max Drawdown
                    </span>
                  </div>
                  <div className="text-2xl font-bold text-semantic-negative tabular-nums">
                    {results.max_drawdown.toFixed(2)}%
                  </div>
                </div>

                <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Award className="w-4 h-4 text-text-secondary" />
                    <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                      Win Rate
                    </span>
                  </div>
                  <div className="text-2xl font-bold text-text-primary tabular-nums">
                    {results.win_rate.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Equity Curve */}
              <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Equity Curve</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={equityCurveData}>
                    <defs>
                      <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2962FF" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#2962FF" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2A2E39" />
                    <XAxis
                      dataKey="day"
                      stroke="#848E9C"
                      style={{ fontSize: '12px' }}
                      label={{ value: 'Days', position: 'insideBottom', offset: -5 }}
                    />
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
                      formatter={(value: number) => [`$${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}`, 'Equity']}
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

              {/* Additional Stats */}
              <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">Statistics</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Total Trades</span>
                    <span className="text-text-primary font-semibold tabular-nums">{results.total_trades}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Final Equity</span>
                    <span className="text-text-primary font-semibold tabular-nums">
                      ${results.final_equity.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Execution Time</span>
                    <span className="text-text-primary font-semibold tabular-nums">
                      {results.execution_time.toFixed(2)}s
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Initial Capital</span>
                    <span className="text-text-primary font-semibold tabular-nums">
                      ${parseFloat(initialCapital).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
