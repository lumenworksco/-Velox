import apiClient from './client'

export interface PortfolioSummary {
  total_value: number
  cash: number
  equity_value: number
  day_pnl: number
  day_pnl_percent: number
  total_pnl: number
  total_pnl_percent: number
  buying_power: number
}

export interface EquityPoint {
  date: string
  equity: number
}

export const getPortfolioSummary = async (): Promise<PortfolioSummary> => {
  return apiClient.get('/portfolio/summary')
}

export const getEquityHistory = async (days: number = 30): Promise<EquityPoint[]> => {
  return apiClient.get(`/portfolio/history?days=${days}`)
}

export const getPerformanceMetrics = async () => {
  return apiClient.get('/portfolio/performance')
}
