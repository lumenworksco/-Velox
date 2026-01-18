import apiClient from './client'

export interface PerformanceMetrics {
  total_return: number
  sharpe_ratio: number
  max_drawdown: number
  win_rate: number
  profit_factor: number
  total_trades: number
  avg_trade_return: number
  best_trade: number
  worst_trade: number
  avg_win: number
  avg_loss: number
  consecutive_wins: number
  consecutive_losses: number
  recovery_factor: number
  calmar_ratio: number
  sortino_ratio: number
}

export interface EquityPoint {
  timestamp: string
  equity: number
  daily_return: number
}

export interface Trade {
  trade_id: string
  symbol: string
  side: 'buy' | 'sell'
  quantity: number
  entry_price: number
  exit_price: number
  entry_time: string
  exit_time: string
  pnl: number
  pnl_percent: number
  strategy: string
  duration_hours: number
}

export interface MonthlyReturns {
  [year: string]: {
    [month: string]: number
  }
}

export interface RiskMetrics {
  var_95: number
  var_99: number
  cvar_95: number
  beta: number
  alpha: number
  correlation_to_spy: number
  volatility: number
  downside_deviation: number
}

export const getPerformanceMetrics = async (
  startDate?: string,
  endDate?: string
): Promise<PerformanceMetrics> => {
  return apiClient.get('/analytics/performance', {
    params: { start_date: startDate, end_date: endDate }
  })
}

export const getEquityCurve = async (
  startDate?: string,
  endDate?: string
): Promise<EquityPoint[]> => {
  return apiClient.get('/analytics/equity-curve', {
    params: { start_date: startDate, end_date: endDate }
  })
}

export const getTradeHistory = async (
  limit?: number,
  offset?: number
): Promise<{ trades: Trade[], total: number }> => {
  return apiClient.get('/analytics/trades', {
    params: { limit, offset }
  })
}

export const getMonthlyReturns = async (): Promise<MonthlyReturns> => {
  return apiClient.get('/analytics/monthly-returns')
}

export const getRiskMetrics = async (): Promise<RiskMetrics> => {
  return apiClient.get('/analytics/risk')
}
