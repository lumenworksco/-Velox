import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, TrendingUp, TrendingDown, Activity, X } from 'lucide-react'
import { getQuote, getHistory, searchSymbols } from '../api/market'
import { getPositions, getOrders, closePosition, cancelOrder } from '../api/trading'
import CandlestickChart from '../components/CandlestickChart'
import OrderEntry from '../components/OrderEntry'
import { CandlestickData, Time } from 'lightweight-charts'

export default function Trading() {
  const [symbol, setSymbol] = useState('AAPL')
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearch, setShowSearch] = useState(false)

  const queryClient = useQueryClient()

  const closePositionMutation = useMutation({
    mutationFn: closePosition,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] })
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    },
  })

  const cancelOrderMutation = useMutation({
    mutationFn: cancelOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] })
    },
  })

  const { data: quote } = useQuery({
    queryKey: ['quote', symbol],
    queryFn: () => getQuote(symbol),
    refetchInterval: 2000,
  })

  const { data: historyData } = useQuery({
    queryKey: ['history', symbol],
    queryFn: () => getHistory(symbol, '1D', 100),
  })

  const { data: positions } = useQuery({
    queryKey: ['positions'],
    queryFn: getPositions,
    refetchInterval: 5000,
  })

  const { data: orders } = useQuery({
    queryKey: ['orders'],
    queryFn: () => getOrders(),
    refetchInterval: 3000,
  })

  const { data: searchResults } = useQuery({
    queryKey: ['search', searchQuery],
    queryFn: () => searchSymbols(searchQuery),
    enabled: searchQuery.length > 0,
  })

  const chartData: CandlestickData<Time>[] = historyData?.map((bar: any) => ({
    time: Math.floor(new Date(bar.timestamp).getTime() / 1000) as Time,
    open: bar.open,
    high: bar.high,
    low: bar.low,
    close: bar.close,
  })) || []

  const isPositive = quote && quote.change >= 0

  return (
    <div style={{ height: '100%', width: '100%', display: 'grid', gridTemplateRows: 'auto 1fr', backgroundColor: '#0d1117', overflow: 'hidden' }}>
      {/* Header with Symbol Search */}
      <div style={{ backgroundColor: '#161b22', borderBottom: '1px solid #30363d', padding: '16px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Symbol Info */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <div>
              <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#c9d1d9', margin: 0 }}>{symbol}</h1>
              {quote && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '4px' }}>
                  <span style={{ fontSize: '28px', fontWeight: 700, color: '#c9d1d9', fontVariantNumeric: 'tabular-nums' }}>
                    ${quote.price.toFixed(2)}
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '18px', fontWeight: 600, color: isPositive ? '#3fb950' : '#f85149' }}>
                    {isPositive ? <TrendingUp style={{ width: '20px', height: '20px' }} /> : <TrendingDown style={{ width: '20px', height: '20px' }} />}
                    <span style={{ fontVariantNumeric: 'tabular-nums' }}>
                      {isPositive ? '+' : ''}{quote.change.toFixed(2)} ({isPositive ? '+' : ''}{quote.change_percent.toFixed(2)}%)
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Quote Details */}
            {quote && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '24px', fontSize: '14px' }}>
                <div>
                  <div style={{ color: '#8b949e', fontSize: '11px', fontFamily: 'monospace' }}>VOLUME</div>
                  <div style={{ color: '#c9d1d9', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
                    {(quote.volume / 1000000).toFixed(2)}M
                  </div>
                </div>
                {quote.bid && (
                  <div>
                    <div style={{ color: '#8b949e', fontSize: '11px', fontFamily: 'monospace' }}>BID</div>
                    <div style={{ color: '#c9d1d9', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>${quote.bid.toFixed(2)}</div>
                  </div>
                )}
                {quote.ask && (
                  <div>
                    <div style={{ color: '#8b949e', fontSize: '11px', fontFamily: 'monospace' }}>ASK</div>
                    <div style={{ color: '#c9d1d9', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>${quote.ask.toFixed(2)}</div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Symbol Search */}
          <div style={{ position: 'relative' }}>
            <div style={{ position: 'relative' }}>
              <Search style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', width: '20px', height: '20px', color: '#8b949e' }} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  setShowSearch(e.target.value.length > 0)
                }}
                onFocus={() => setShowSearch(searchQuery.length > 0)}
                placeholder="Search symbol..."
                style={{
                  width: '256px',
                  backgroundColor: '#0d1117',
                  border: '1px solid #30363d',
                  borderRadius: '6px',
                  padding: '8px 16px 8px 40px',
                  color: '#c9d1d9',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
            </div>

            {/* Search Results Dropdown */}
            {showSearch && searchResults && searchResults.length > 0 && (
              <div style={{
                position: 'absolute',
                top: '100%',
                marginTop: '8px',
                width: '100%',
                backgroundColor: '#161b22',
                border: '1px solid #30363d',
                borderRadius: '6px',
                boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
                zIndex: 10,
                maxHeight: '256px',
                overflowY: 'auto'
              }}>
                {searchResults.map((result: any) => (
                  <button
                    key={result.symbol}
                    onClick={() => {
                      setSymbol(result.symbol)
                      setSearchQuery('')
                      setShowSearch(false)
                    }}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      textAlign: 'left',
                      backgroundColor: 'transparent',
                      border: 'none',
                      borderBottom: '1px solid #30363d',
                      cursor: 'pointer',
                      transition: 'background-color 0.1s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#21262d'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <div style={{ fontWeight: 600, color: '#c9d1d9' }}>{result.symbol}</div>
                    <div style={{ fontSize: '13px', color: '#8b949e' }}>{result.name}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1px', backgroundColor: '#30363d', overflow: 'hidden' }}>
        {/* Left Column - Chart & Orders */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1px', backgroundColor: '#30363d', overflow: 'hidden' }}>
          {/* Chart */}
          <div style={{ flex: 1, backgroundColor: '#0d1117', minHeight: '400px', padding: '16px', display: 'flex', flexDirection: 'column' }}>
            <CandlestickChart data={chartData} symbol={symbol} />
          </div>

          {/* Open Orders */}
          <div style={{ backgroundColor: '#0d1117', maxHeight: '300px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ borderBottom: '1px solid #30363d', padding: '12px 16px' }}>
              <h3 style={{ fontSize: '12px', fontWeight: 700, color: '#c9d1d9', letterSpacing: '0.03em', margin: 0 }}>OPEN ORDERS</h3>
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
              {orders && orders.length > 0 ? (
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #30363d' }}>
                      <th style={{ textAlign: 'left', padding: '8px 0', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>Symbol</th>
                      <th style={{ textAlign: 'left', padding: '8px 0', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>Side</th>
                      <th style={{ textAlign: 'right', padding: '8px 0', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>Qty</th>
                      <th style={{ textAlign: 'right', padding: '8px 0', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>Price</th>
                      <th style={{ textAlign: 'left', padding: '8px 0', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>Status</th>
                      <th style={{ textAlign: 'right', padding: '8px 0', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.map((order) => (
                      <tr key={order.order_id} style={{ borderBottom: '1px solid rgba(48, 54, 61, 0.5)' }}>
                        <td style={{ padding: '12px 0', color: '#c9d1d9', fontWeight: 600 }}>{order.symbol}</td>
                        <td style={{ padding: '12px 0' }}>
                          <span style={{
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '11px',
                            fontWeight: 600,
                            backgroundColor: order.side === 'buy' ? 'rgba(63, 185, 80, 0.2)' : 'rgba(248, 81, 73, 0.2)',
                            color: order.side === 'buy' ? '#3fb950' : '#f85149'
                          }}>
                            {order.side.toUpperCase()}
                          </span>
                        </td>
                        <td style={{ padding: '12px 0', textAlign: 'right', color: '#c9d1d9', fontVariantNumeric: 'tabular-nums' }}>{order.quantity}</td>
                        <td style={{ padding: '12px 0', textAlign: 'right', color: '#c9d1d9', fontVariantNumeric: 'tabular-nums' }}>
                          ${order.avg_price?.toFixed(2) || '—'}
                        </td>
                        <td style={{ padding: '12px 0', color: '#8b949e' }}>{order.status}</td>
                        <td style={{ padding: '12px 0', textAlign: 'right' }}>
                          {['pending', 'new', 'accepted', 'partially_filled'].includes(order.status) ? (
                            <button
                              onClick={() => cancelOrderMutation.mutate(order.order_id)}
                              disabled={cancelOrderMutation.isPending}
                              style={{
                                padding: '4px 8px',
                                borderRadius: '4px',
                                border: 'none',
                                backgroundColor: '#f85149',
                                color: '#ffffff',
                                fontSize: '11px',
                                fontWeight: 600,
                                cursor: cancelOrderMutation.isPending ? 'not-allowed' : 'pointer',
                                opacity: cancelOrderMutation.isPending ? 0.5 : 1
                              }}
                            >
                              <X style={{ width: '12px', height: '12px' }} />
                            </button>
                          ) : (
                            <span style={{ color: '#8b949e', fontSize: '11px' }}>—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div style={{ textAlign: 'center', padding: '32px 0', color: '#8b949e' }}>
                  No open orders
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Sidebar - Order Entry & Positions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1px', backgroundColor: '#30363d', overflow: 'hidden' }}>
          {/* Order Entry */}
          <div style={{ backgroundColor: '#0d1117' }}>
            <OrderEntry symbol={symbol} currentPrice={quote?.price} />
          </div>

          {/* Current Positions */}
          <div style={{ flex: 1, backgroundColor: '#0d1117', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
            <div style={{ borderBottom: '1px solid #30363d', padding: '12px 16px', display: 'flex', alignItems: 'center' }}>
              <Activity style={{ width: '16px', height: '16px', marginRight: '8px', color: '#8b949e' }} />
              <h3 style={{ fontSize: '12px', fontWeight: 700, color: '#c9d1d9', letterSpacing: '0.03em', margin: 0 }}>POSITIONS</h3>
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
              {positions && positions.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {positions.map((position) => {
                    const isProfitable = position.unrealized_pnl >= 0
                    return (
                      <div key={position.symbol} style={{ backgroundColor: '#161b22', borderRadius: '6px', padding: '16px', border: '1px solid #30363d' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                          <div style={{ fontWeight: 600, color: '#c9d1d9' }}>{position.symbol}</div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{ fontSize: '13px', fontWeight: 600, color: isProfitable ? '#3fb950' : '#f85149' }}>
                              {isProfitable ? '+' : ''}{position.unrealized_pnl_percent.toFixed(2)}%
                            </div>
                            <button
                              onClick={() => closePositionMutation.mutate(position.symbol)}
                              disabled={closePositionMutation.isPending}
                              style={{
                                padding: '4px 8px',
                                borderRadius: '4px',
                                border: '1px solid #f85149',
                                backgroundColor: 'transparent',
                                color: '#f85149',
                                fontSize: '11px',
                                fontWeight: 600,
                                cursor: closePositionMutation.isPending ? 'not-allowed' : 'pointer',
                                opacity: closePositionMutation.isPending ? 0.5 : 1
                              }}
                            >
                              CLOSE
                            </button>
                          </div>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '12px' }}>
                          <div>
                            <div style={{ color: '#8b949e', marginBottom: '2px' }}>Qty</div>
                            <div style={{ color: '#c9d1d9', fontFamily: 'monospace' }}>{position.quantity}</div>
                          </div>
                          <div>
                            <div style={{ color: '#8b949e', marginBottom: '2px' }}>Avg Price</div>
                            <div style={{ color: '#c9d1d9', fontFamily: 'monospace' }}>${position.avg_entry_price.toFixed(2)}</div>
                          </div>
                          <div>
                            <div style={{ color: '#8b949e', marginBottom: '2px' }}>Market Value</div>
                            <div style={{ color: '#c9d1d9', fontFamily: 'monospace' }}>${position.market_value.toFixed(2)}</div>
                          </div>
                          <div>
                            <div style={{ color: '#8b949e', marginBottom: '2px' }}>P&L</div>
                            <div style={{ fontFamily: 'monospace', fontWeight: 600, color: isProfitable ? '#3fb950' : '#f85149' }}>
                              {isProfitable ? '+' : ''}${position.unrealized_pnl.toFixed(2)}
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '32px 0', color: '#8b949e', fontSize: '14px' }}>
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
