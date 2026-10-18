import apiClient from './client'

export interface Strategy {
  strategy_id: string
  name: string
  description: string
  status: 'active' | 'paused' | 'stopped'
  symbols: string[]
  timeframe: string
  risk_per_trade: number
  max_positions: number
  created_at: string
  updated_at: string
}

export interface StrategyPerformance {
  strategy_id: string
  total_return: number
  sharpe_ratio: number
  win_rate: number
  total_trades: number
  active_positions: number
  daily_pnl: number
  daily_pnl_percent: number
}

export interface StrategyConfig {
  name: string
  strategy_type: string
  symbols: string[]
  timeframe: string
  risk_per_trade: number
  max_positions: number
  parameters: Record<string, any>
}

export interface StrategySignal {
  signal_id: string
  strategy_id: string
  symbol: string
  signal: 'buy' | 'sell' | 'hold'
  confidence: number
  price: number
  timestamp: string
  reasoning: string
}

export const getStrategies = async (): Promise<Strategy[]> => {
  return apiClient.get('/strategies')
}

export const getStrategy = async (strategyId: string): Promise<Strategy> => {
  return apiClient.get(`/strategies/${strategyId}`)
}

export const createStrategy = async (config: StrategyConfig): Promise<Strategy> => {
  return apiClient.post('/strategies', config)
}

export const updateStrategy = async (
  strategyId: string,
  config: Partial<StrategyConfig>
): Promise<Strategy> => {
  return apiClient.put(`/strategies/${strategyId}`, config)
}

export const deleteStrategy = async (strategyId: string): Promise<void> => {
  return apiClient.delete(`/strategies/${strategyId}`)
}

export const startStrategy = async (strategyId: string): Promise<void> => {
  return apiClient.post(`/strategies/${strategyId}/start`)
}

export const pauseStrategy = async (strategyId: string): Promise<void> => {
  return apiClient.post(`/strategies/${strategyId}/pause`)
}

export const stopStrategy = async (strategyId: string): Promise<void> => {
  return apiClient.post(`/strategies/${strategyId}/stop`)
}

export const getStrategyPerformance = async (
  strategyId: string
): Promise<StrategyPerformance> => {
  return apiClient.get(`/strategies/${strategyId}/performance`)
}

export const getStrategySignals = async (
  strategyId: string,
  limit?: number
): Promise<StrategySignal[]> => {
  return apiClient.get(`/strategies/${strategyId}/signals`, {
    params: { limit }
  })
}

export const getAvailableStrategyTypes = async (): Promise<
  Array<{
    id: string
    name: string
    description: string
    parameters: Array<{ name: string; type: string; default: any; description: string }>
  }>
> => {
  return apiClient.get('/strategies/types')
}
