import apiClient from './client'

export interface OrderRequest {
  symbol: string
  side: 'buy' | 'sell'
  quantity: number
  order_type: 'market' | 'limit' | 'stop'
  limit_price?: number
  stop_price?: number
}

export interface Order {
  order_id: string
  status: string
  symbol: string
  side: string
  quantity: number
  filled_qty: number
  avg_price: number | null
  created_at: string
}

export interface Position {
  symbol: string
  quantity: number
  avg_entry_price: number
  current_price: number
  market_value: number
  unrealized_pnl: number
  unrealized_pnl_percent: number
}

export const placeOrder = async (order: OrderRequest): Promise<Order> => {
  return apiClient.post('/trading/orders', order)
}

export const getOrders = async (status?: string): Promise<Order[]> => {
  return apiClient.get('/trading/orders', {
    params: status ? { status } : undefined
  })
}

export const cancelOrder = async (orderId: string): Promise<void> => {
  return apiClient.delete(`/trading/orders/${orderId}`)
}

export const getPositions = async (): Promise<Position[]> => {
  return apiClient.get('/trading/positions')
}

export const closePosition = async (symbol: string): Promise<void> => {
  return apiClient.post(`/trading/positions/${symbol}/close`)
}
