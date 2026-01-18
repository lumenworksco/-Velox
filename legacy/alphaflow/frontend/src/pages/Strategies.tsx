import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Play,
  Pause,
  Square,
  Plus,
  TrendingUp,
  TrendingDown,
  Activity,
  Award,
  Target,
  Settings as SettingsIcon,
  Trash2,
  Edit,
  Signal,
} from 'lucide-react'
import {
  getStrategies,
  getStrategyPerformance,
  getStrategySignals,
  startStrategy,
  pauseStrategy,
  stopStrategy,
  deleteStrategy,
  getAvailableStrategyTypes,
  createStrategy,
  type Strategy,
  type StrategyConfig,
} from '../api/strategies'

export default function Strategies() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Fetch all strategies
  const { data: strategies } = useQuery({
    queryKey: ['strategies'],
    queryFn: getStrategies,
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  // Fetch performance for selected strategy
  const { data: performance } = useQuery({
    queryKey: ['strategy-performance', selectedStrategy],
    queryFn: () => getStrategyPerformance(selectedStrategy!),
    enabled: !!selectedStrategy,
    refetchInterval: 2000,
  })

  // Fetch signals for selected strategy
  const { data: signals } = useQuery({
    queryKey: ['strategy-signals', selectedStrategy],
    queryFn: () => getStrategySignals(selectedStrategy!, 20),
    enabled: !!selectedStrategy,
    refetchInterval: 2000,
  })

  // Mutations
  const startMutation = useMutation({
    mutationFn: startStrategy,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['strategies'] }),
  })

  const pauseMutation = useMutation({
    mutationFn: pauseStrategy,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['strategies'] }),
  })

  const stopMutation = useMutation({
    mutationFn: stopStrategy,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['strategies'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteStrategy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
      if (selectedStrategy) {
        setSelectedStrategy(null)
      }
    },
  })

  const handleStrategyAction = (strategyId: string, action: 'start' | 'pause' | 'stop') => {
    switch (action) {
      case 'start':
        startMutation.mutate(strategyId)
        break
      case 'pause':
        pauseMutation.mutate(strategyId)
        break
      case 'stop':
        stopMutation.mutate(strategyId)
        break
    }
  }

  const getStatusColor = (status: Strategy['status']) => {
    switch (status) {
      case 'active':
        return 'text-semantic-positive bg-semantic-positive/20'
      case 'paused':
        return 'text-accent-amber bg-accent-amber/20'
      case 'stopped':
        return 'text-text-tertiary bg-primary-elevated'
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Trading Strategies</h1>
          <p className="text-text-secondary mt-1">Deploy and manage your algorithmic trading strategies</p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-accent-blue hover:bg-accent-blue-hover text-white font-semibold px-6 py-3 rounded-lg transition-colors flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>New Strategy</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Strategy List */}
        <div className="lg:col-span-1 space-y-4">
          {strategies?.map((strategy) => (
            <div
              key={strategy.strategy_id}
              onClick={() => setSelectedStrategy(strategy.strategy_id)}
              className={`bg-primary-surface rounded-lg border cursor-pointer transition-all ${
                selectedStrategy === strategy.strategy_id
                  ? 'border-accent-blue shadow-lg'
                  : 'border-primary-border hover:border-accent-blue/50'
              }`}
            >
              <div className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-text-primary">{strategy.name}</h3>
                    <p className="text-sm text-text-secondary mt-1">{strategy.description}</p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                      strategy.status
                    )}`}
                  >
                    {strategy.status.toUpperCase()}
                  </span>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Symbols</span>
                    <span className="text-text-primary font-medium">
                      {strategy.symbols.join(', ')}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Timeframe</span>
                    <span className="text-text-primary font-medium">{strategy.timeframe}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Risk/Trade</span>
                    <span className="text-text-primary font-medium">
                      {strategy.risk_per_trade}%
                    </span>
                  </div>
                </div>

                {/* Control Buttons */}
                <div className="flex items-center space-x-2 mt-4 pt-4 border-t border-primary-border">
                  {strategy.status === 'stopped' && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleStrategyAction(strategy.strategy_id, 'start')
                      }}
                      className="flex-1 bg-semantic-positive hover:bg-semantic-positive/90 text-white font-semibold py-2 rounded-lg transition-colors flex items-center justify-center space-x-2"
                    >
                      <Play className="w-4 h-4" />
                      <span>Start</span>
                    </button>
                  )}

                  {strategy.status === 'active' && (
                    <>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleStrategyAction(strategy.strategy_id, 'pause')
                        }}
                        className="flex-1 bg-accent-amber hover:bg-accent-amber/90 text-white font-semibold py-2 rounded-lg transition-colors flex items-center justify-center space-x-2"
                      >
                        <Pause className="w-4 h-4" />
                        <span>Pause</span>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleStrategyAction(strategy.strategy_id, 'stop')
                        }}
                        className="flex-1 bg-semantic-negative hover:bg-semantic-negative/90 text-white font-semibold py-2 rounded-lg transition-colors flex items-center justify-center space-x-2"
                      >
                        <Square className="w-4 h-4" />
                        <span>Stop</span>
                      </button>
                    </>
                  )}

                  {strategy.status === 'paused' && (
                    <>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleStrategyAction(strategy.strategy_id, 'start')
                        }}
                        className="flex-1 bg-semantic-positive hover:bg-semantic-positive/90 text-white font-semibold py-2 rounded-lg transition-colors flex items-center justify-center space-x-2"
                      >
                        <Play className="w-4 h-4" />
                        <span>Resume</span>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleStrategyAction(strategy.strategy_id, 'stop')
                        }}
                        className="flex-1 bg-semantic-negative hover:bg-semantic-negative/90 text-white font-semibold py-2 rounded-lg transition-colors flex items-center justify-center space-x-2"
                      >
                        <Square className="w-4 h-4" />
                        <span>Stop</span>
                      </button>
                    </>
                  )}

                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      if (
                        confirm(
                          `Are you sure you want to delete strategy "${strategy.name}"? This cannot be undone.`
                        )
                      ) {
                        deleteMutation.mutate(strategy.strategy_id)
                      }
                    }}
                    className="bg-semantic-negative/20 hover:bg-semantic-negative/30 text-semantic-negative font-semibold p-2 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}

          {strategies?.length === 0 && (
            <div className="bg-primary-surface rounded-lg border border-primary-border p-8 text-center">
              <Activity className="w-12 h-12 text-text-tertiary mx-auto mb-3" />
              <p className="text-text-secondary">No strategies yet</p>
              <p className="text-text-tertiary text-sm mt-1">Create your first strategy to get started</p>
            </div>
          )}
        </div>

        {/* Strategy Details */}
        <div className="lg:col-span-2 space-y-6">
          {selectedStrategy && performance ? (
            <>
              {/* Performance Metrics */}
              <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-text-secondary" />
                    <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                      Total Return
                    </span>
                  </div>
                  <div
                    className={`text-2xl font-bold tabular-nums ${
                      performance.total_return >= 0
                        ? 'text-semantic-positive'
                        : 'text-semantic-negative'
                    }`}
                  >
                    {performance.total_return >= 0 ? '+' : ''}
                    {performance.total_return.toFixed(2)}%
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
                    {performance.sharpe_ratio.toFixed(2)}
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
                    {performance.win_rate.toFixed(1)}%
                  </div>
                </div>

                <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Target className="w-4 h-4 text-text-secondary" />
                    <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                      Total Trades
                    </span>
                  </div>
                  <div className="text-2xl font-bold text-text-primary tabular-nums">
                    {performance.total_trades}
                  </div>
                </div>

                <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-text-secondary" />
                    <span className="text-xs uppercase tracking-wider text-text-secondary font-semibold">
                      Daily P&L
                    </span>
                  </div>
                  <div
                    className={`text-2xl font-bold tabular-nums ${
                      performance.daily_pnl >= 0 ? 'text-semantic-positive' : 'text-semantic-negative'
                    }`}
                  >
                    {performance.daily_pnl >= 0 ? '+' : ''}${performance.daily_pnl.toFixed(2)}
                  </div>
                  <div
                    className={`text-sm tabular-nums ${
                      performance.daily_pnl_percent >= 0
                        ? 'text-semantic-positive'
                        : 'text-semantic-negative'
                    }`}
                  >
                    {performance.daily_pnl_percent >= 0 ? '+' : ''}
                    {performance.daily_pnl_percent.toFixed(2)}%
                  </div>
                </div>
              </div>

              {/* Recent Signals */}
              {signals && signals.length > 0 && (
                <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
                  <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center space-x-2">
                    <Signal className="w-5 h-5" />
                    <span>Recent Signals</span>
                  </h3>
                  <div className="space-y-3">
                    {signals.map((signal) => (
                      <div
                        key={signal.signal_id}
                        className="bg-primary-elevated rounded-lg p-4 hover:bg-primary-hover transition-colors"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <span className="text-text-primary font-bold">{signal.symbol}</span>
                            <span
                              className={`px-3 py-1 rounded-full text-xs font-bold ${
                                signal.signal === 'buy'
                                  ? 'bg-semantic-positive/20 text-semantic-positive'
                                  : signal.signal === 'sell'
                                  ? 'bg-semantic-negative/20 text-semantic-negative'
                                  : 'bg-primary-border text-text-secondary'
                              }`}
                            >
                              {signal.signal.toUpperCase()}
                            </span>
                            <span className="text-text-secondary text-sm">
                              ${signal.price.toFixed(2)}
                            </span>
                          </div>
                          <div className="flex items-center space-x-4">
                            <div className="text-right">
                              <div className="text-text-secondary text-xs">Confidence</div>
                              <div className="text-text-primary font-semibold tabular-nums">
                                {(signal.confidence * 100).toFixed(0)}%
                              </div>
                            </div>
                            <div className="text-text-tertiary text-sm">
                              {new Date(signal.timestamp).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                        <p className="text-text-secondary text-sm">{signal.reasoning}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="bg-primary-surface rounded-lg border border-primary-border p-12 flex flex-col items-center justify-center text-center h-full">
              <Activity className="w-16 h-16 text-text-tertiary mb-4" />
              <h3 className="text-xl font-semibold text-text-primary mb-2">
                No Strategy Selected
              </h3>
              <p className="text-text-secondary">
                Select a strategy from the list to view its performance and signals
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
