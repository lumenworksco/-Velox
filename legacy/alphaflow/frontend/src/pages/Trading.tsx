import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, TrendingUp, TrendingDown, Activity } from 'lucide-react'
import { getQuote, getHistory, searchSymbols } from '../api/market'
import { getPositions, getOrders } from '../api/trading'
import CandlestickChart from '../components/CandlestickChart'
import OrderEntry from '../components/OrderEntry'
import { CandlestickData, Time } from 'lightweight-charts'

export default function Trading() {
  const [symbol, setSymbol] = useState('AAPL')
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearch, setShowSearch] = useState(false)

  // Fetch current quote
  const { data: quote } = useQuery({
    queryKey: ['quote', symbol],
    queryFn: () => getQuote(symbol),
    refetchInterval: 2000, // Refresh every 2 seconds
  })

  // Fetch historical data for chart
  const { data: historyData } = useQuery({
    queryKey: ['history', symbol],
    queryFn: () => getHistory(symbol, '1D', 100),
  })

  // Fetch positions
  const { data: positions } = useQuery({
    queryKey: ['positions'],
    queryFn: getPositions,
    refetchInterval: 5000,
  })

  // Fetch orders
  const { data: orders } = useQuery({
    queryKey: ['orders'],
    queryFn: () => getOrders(),
    refetchInterval: 3000,
  })

  // Search symbols
  const { data: searchResults } = useQuery({
    queryKey: ['search', searchQuery],
    queryFn: () => searchSymbols(searchQuery),
    enabled: searchQuery.length > 0,
  })

  // Convert history data to candlestick format
  const chartData: CandlestickData<Time>[] = historyData?.map((bar: any) => ({
    time: Math.floor(new Date(bar.timestamp).getTime() / 1000) as Time,
    open: bar.open,
    high: bar.high,
    low: bar.low,
    close: bar.close,
  })) || []

  const isPositive = quote && quote.change >= 0

  return (
    <div className="h-full flex flex-col">
      {/* Header with Symbol Search */}
      <div className="bg-primary-surface border-b border-primary-border px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Symbol Info */}
          <div className="flex items-center space-x-6">
            <div>
              <h1 className="text-2xl font-bold text-text-primary">{symbol}</h1>
              {quote && (
                <div className="flex items-center space-x-3 mt-1">
                  <span className="text-3xl font-bold text-text-primary tabular-nums">
                    ${quote.price.toFixed(2)}
                  </span>
                  <div className={`flex items-center space-x-1 text-lg font-semibold ${
                    isPositive ? 'text-semantic-positive' : 'text-semantic-negative'
                  }`}>
                    {isPositive ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
                    <span className="tabular-nums">
                      {isPositive ? '+' : ''}{quote.change.toFixed(2)} ({isPositive ? '+' : ''}{quote.change_percent.toFixed(2)}%)
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Quote Details */}
            {quote && (
              <div className="flex items-center space-x-6 text-sm">
                <div>
                  <div className="text-text-tertiary">Volume</div>
                  <div className="text-text-primary font-semibold tabular-nums">
                    {(quote.volume / 1000000).toFixed(2)}M
                  </div>
                </div>
                {quote.bid && (
                  <div>
                    <div className="text-text-tertiary">Bid</div>
                    <div className="text-text-primary font-semibold tabular-nums">${quote.bid.toFixed(2)}</div>
                  </div>
                )}
                {quote.ask && (
                  <div>
                    <div className="text-text-tertiary">Ask</div>
                    <div className="text-text-primary font-semibold tabular-nums">${quote.ask.toFixed(2)}</div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Symbol Search */}
          <div className="relative">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-tertiary" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  setShowSearch(e.target.value.length > 0)
                }}
                onFocus={() => setShowSearch(searchQuery.length > 0)}
                placeholder="Search symbol..."
                className="w-64 bg-primary-elevated border border-primary-border rounded-lg py-2 pl-10 pr-4 text-text-primary placeholder-text-tertiary focus:outline-none focus:border-accent-blue"
              />
            </div>

            {/* Search Results Dropdown */}
            {showSearch && searchResults && searchResults.length > 0 && (
              <div className="absolute top-full mt-2 w-full bg-primary-elevated border border-primary-border rounded-lg shadow-lg z-10 max-h-64 overflow-y-auto">
                {searchResults.map((result: any) => (
                  <button
                    key={result.symbol}
                    onClick={() => {
                      setSymbol(result.symbol)
                      setSearchQuery('')
                      setShowSearch(false)
                    }}
                    className="w-full px-4 py-3 text-left hover:bg-primary-hover transition-colors border-b border-primary-border last:border-b-0"
                  >
                    <div className="font-semibold text-text-primary">{result.symbol}</div>
                    <div className="text-sm text-text-secondary">{result.name}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
          {/* Chart Area - 2/3 width */}
          <div className="lg:col-span-2 space-y-6">
            {/* Chart */}
            <div className="bg-primary-surface rounded-lg border border-primary-border p-4">
              <CandlestickChart data={chartData} symbol={symbol} />
            </div>

            {/* Open Orders */}
            <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">Open Orders</h3>
              {orders && orders.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-primary-border">
                        <th className="text-left py-2 text-xs uppercase tracking-wider text-text-secondary font-bold">Symbol</th>
                        <th className="text-left py-2 text-xs uppercase tracking-wider text-text-secondary font-bold">Side</th>
                        <th className="text-right py-2 text-xs uppercase tracking-wider text-text-secondary font-bold">Qty</th>
                        <th className="text-right py-2 text-xs uppercase tracking-wider text-text-secondary font-bold">Price</th>
                        <th className="text-left py-2 text-xs uppercase tracking-wider text-text-secondary font-bold">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orders.map((order) => (
                        <tr key={order.order_id} className="border-b border-primary-border/50">
                          <td className="py-3 text-text-primary font-semibold">{order.symbol}</td>
                          <td className="py-3">
                            <span className={`px-2 py-1 rounded text-xs font-semibold ${
                              order.side === 'buy'
                                ? 'bg-semantic-positive/20 text-semantic-positive'
                                : 'bg-semantic-negative/20 text-semantic-negative'
                            }`}>
                              {order.side.toUpperCase()}
                            </span>
                          </td>
                          <td className="py-3 text-right text-text-primary tabular-nums">{order.quantity}</td>
                          <td className="py-3 text-right text-text-primary tabular-nums">
                            ${order.avg_price?.toFixed(2) || '—'}
                          </td>
                          <td className="py-3 text-text-secondary">{order.status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-text-secondary">
                  No open orders
                </div>
              )}
            </div>
          </div>

          {/* Right Sidebar - Order Entry & Positions */}
          <div className="space-y-6">
            {/* Order Entry */}
            <OrderEntry symbol={symbol} currentPrice={quote?.price} />

            {/* Current Positions */}
            <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2" />
                Positions
              </h3>
              {positions && positions.length > 0 ? (
                <div className="space-y-3">
                  {positions.map((position) => {
                    const isProfitable = position.unrealized_pnl >= 0
                    return (
                      <div key={position.symbol} className="bg-primary-elevated rounded-lg p-4 border border-primary-border">
                        <div className="flex justify-between items-start mb-2">
                          <div className="font-semibold text-text-primary">{position.symbol}</div>
                          <div className={`text-sm font-semibold ${
                            isProfitable ? 'text-semantic-positive' : 'text-semantic-negative'
                          }`}>
                            {isProfitable ? '+' : ''}{position.unrealized_pnl_percent.toFixed(2)}%
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          <div>
                            <div className="text-text-tertiary">Qty</div>
                            <div className="text-text-primary font-mono">{position.quantity}</div>
                          </div>
                          <div>
                            <div className="text-text-tertiary">Avg Price</div>
                            <div className="text-text-primary font-mono">${position.avg_entry_price.toFixed(2)}</div>
                          </div>
                          <div>
                            <div className="text-text-tertiary">Market Value</div>
                            <div className="text-text-primary font-mono">${position.market_value.toFixed(2)}</div>
                          </div>
                          <div>
                            <div className="text-text-tertiary">P&L</div>
                            <div className={`font-mono font-semibold ${
                              isProfitable ? 'text-semantic-positive' : 'text-semantic-negative'
                            }`}>
                              {isProfitable ? '+' : ''}${position.unrealized_pnl.toFixed(2)}
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-text-secondary text-sm">
                  No open positions
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
