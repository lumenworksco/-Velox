import { useState, useEffect } from 'react'
import { useWebSocket } from './useWebSocket'

interface Quote {
  symbol: string
  price: number
  bid: number
  ask: number
  volume: number
  timestamp: string
  change: number
  changePercent: number
}

const WS_URL = 'ws://localhost:8000/ws/quotes'

export function useRealtimeQuotes(symbols: string[]) {
  const [quotes, setQuotes] = useState<Record<string, Quote>>({})
  const [priceFlashes, setPriceFlashes] = useState<Record<string, 'up' | 'down' | null>>({})

  const { isConnected, send } = useWebSocket(WS_URL, {
    onMessage: (message) => {
      if (message.type === 'quote') {
        const quote = message.data as Quote

        // Check if price changed for flash animation
        if (quotes[quote.symbol]) {
          const oldPrice = quotes[quote.symbol].price
          const newPrice = quote.price

          if (newPrice > oldPrice) {
            setPriceFlashes((prev) => ({ ...prev, [quote.symbol]: 'up' }))
          } else if (newPrice < oldPrice) {
            setPriceFlashes((prev) => ({ ...prev, [quote.symbol]: 'down' }))
          }

          // Clear flash after animation
          setTimeout(() => {
            setPriceFlashes((prev) => ({ ...prev, [quote.symbol]: null }))
          }, 500)
        }

        setQuotes((prev) => ({
          ...prev,
          [quote.symbol]: quote,
        }))
      }
    },
    onConnect: () => {
      console.log('Connected to realtime quotes')
    },
  })

  useEffect(() => {
    if (isConnected && symbols.length > 0) {
      // Subscribe to symbols
      send({
        type: 'subscribe',
        symbols,
      })
    }

    return () => {
      if (isConnected && symbols.length > 0) {
        // Unsubscribe when component unmounts or symbols change
        send({
          type: 'unsubscribe',
          symbols,
        })
      }
    }
  }, [isConnected, symbols.join(',')])

  return {
    quotes,
    priceFlashes,
    isConnected,
  }
}
