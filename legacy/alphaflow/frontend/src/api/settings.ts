import apiClient from './client'

export interface Settings {
  alpaca_api_key: string | null
  alpaca_secret_key_set: boolean
  paper_trading: boolean
  max_position_size: number
  max_daily_loss: number
  stop_loss_percent: number
  take_profit_percent: number
  dark_mode: boolean
}

export interface APIKeysRequest {
  alpaca_api_key?: string
  alpaca_secret_key?: string
  paper_trading: boolean
}

export interface RiskSettingsRequest {
  max_position_size: number
  max_daily_loss: number
  stop_loss_percent: number
  take_profit_percent: number
}

export const getSettings = async (): Promise<Settings> => {
  return apiClient.get('/settings/')
}

export const updateAPIKeys = async (keys: APIKeysRequest): Promise<void> => {
  return apiClient.put('/settings/api-keys', keys)
}

export const updateRiskSettings = async (risk: RiskSettingsRequest): Promise<void> => {
  return apiClient.put('/settings/risk', risk)
}
