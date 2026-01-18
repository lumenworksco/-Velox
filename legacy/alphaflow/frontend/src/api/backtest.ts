import apiClient from './client'

export interface BacktestRequest {
  symbols: string[]
  strategy: string
  start_date: string
  end_date: string
  initial_capital: number
  commission: number
}

export interface BacktestStatus {
  backtest_id: string
  status: 'running' | 'completed' | 'failed'
  progress: number
  message: string
}

export interface BacktestResult {
  backtest_id: string
  total_return: number
  sharpe_ratio: number
  max_drawdown: number
  win_rate: number
  total_trades: number
  final_equity: number
  execution_time: number
}

export const runBacktest = async (request: BacktestRequest): Promise<BacktestStatus> => {
  return apiClient.post('/backtest/run', request)
}

export const getBacktestStatus = async (backtestId: string): Promise<BacktestStatus> => {
  return apiClient.get(`/backtest/status/${backtestId}`)
}

export const getBacktestResults = async (backtestId: string): Promise<BacktestResult> => {
  return apiClient.get(`/backtest/results/${backtestId}`)
}

export const cancelBacktest = async (backtestId: string): Promise<void> => {
  return apiClient.delete(`/backtest/${backtestId}`)
}
