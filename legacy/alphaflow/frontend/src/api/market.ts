import apiClient from './client'

export interface Quote {
  symbol: string
  price: number
  change: number
  change_percent: number
  volume: number
  high?: number
  low?: number
  bid?: number
  ask?: number
  timestamp: string
}

export const getQuote = async (symbol: string): Promise<Quote> => {
  return apiClient.get(`/market/quote/${symbol}`)
}

export const getQuotes = async (symbols: string[]): Promise<Quote[]> => {
  const params = new URLSearchParams()
  symbols.forEach(s => params.append('symbols', s))
  return apiClient.get(`/market/quotes?${params}`)
}

export const getHistory = async (
  symbol: string,
  timeframe: string = '1D',
  limit: number = 100
) => {
  return apiClient.get(`/market/history/${symbol}`, {
    params: { timeframe, limit }
  })
}

export const searchSymbols = async (query: string) => {
  return apiClient.get(`/market/search`, {
    params: { query }
  })
}
