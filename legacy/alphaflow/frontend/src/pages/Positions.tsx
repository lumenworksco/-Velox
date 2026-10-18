import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Activity, TrendingUp, TrendingDown, X, AlertCircle } from 'lucide-react'
import { getQuote } from '../api/market'

interface Position {
  symbol: string
  strategy_id: string
  shares: number
  entry_price: number
  entry_time: string
  stop_loss: number | null
  take_profit: number | null
  unrealized_pnl: number
  unrealized_pnl_percent: number
}

export default function Positions() {
  const queryClient = useQueryClient()

  // Fetch all positions from strategy execution
  const { data: positions, isLoading } = useQuery({
    queryKey: ['strategy-positions'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/positions/list')
      if (!response.ok) throw new Error('Failed to fetch positions')
      return response.json()
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  // Close position mutation
  const closePositionMutation = useMutation({
    mutationFn: async ({ strategy_id, symbol }: { strategy_id: string; symbol: string }) => {
      const response = await fetch('http://localhost:8000/api/trading/close-position', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy_id, symbol }),
      })
      if (!response.ok) throw new Error('Failed to close position')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategy-positions'] })
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    },
  })

  // Calculate totals
  const totalPositions = positions?.length || 0
  const totalPnL = positions?.reduce((sum: number, pos: Position) => sum + pos.unrealized_pnl, 0) || 0
  const profitablePositions = positions?.filter((pos: Position) => pos.unrealized_pnl > 0).length || 0
  const losingPositions = positions?.filter((pos: Position) => pos.unrealized_pnl < 0).length || 0

  return (
    <div style={{ height: '100%', width: '100%', backgroundColor: '#0d1117', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ backgroundColor: '#161b22', borderBottom: '1px solid #30363d', padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Activity style={{ width: '28px', height: '28px', color: '#58a6ff' }} />
              <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#c9d1d9', margin: 0 }}>Strategy Positions</h1>
            </div>
            <p style={{ fontSize: '14px', color: '#8b949e', marginTop: '8px', marginBottom: 0 }}>
              Live positions managed by automated trading strategies
            </p>
          </div>

          {/* Summary Stats */}
          <div style={{ display: 'flex', gap: '24px' }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: '#8b949e', fontFamily: 'monospace', marginBottom: '4px' }}>TOTAL POSITIONS</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#c9d1d9', fontVariantNumeric: 'tabular-nums' }}>
                {totalPositions}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: '#8b949e', fontFamily: 'monospace', marginBottom: '4px' }}>TOTAL P&L</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: totalPnL >= 0 ? '#3fb950' : '#f85149', fontVariantNumeric: 'tabular-nums' }}>
                {totalPnL >= 0 ? '+' : ''}${totalPnL.toFixed(2)}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: '#8b949e', fontFamily: 'monospace', marginBottom: '4px' }}>WIN/LOSS</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#c9d1d9', fontVariantNumeric: 'tabular-nums' }}>
                <span style={{ color: '#3fb950' }}>{profitablePositions}</span>
                <span style={{ color: '#8b949e', margin: '0 4px' }}>/</span>
                <span style={{ color: '#f85149' }}>{losingPositions}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Positions Table */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '64px 0', color: '#8b949e' }}>
            <div style={{ fontSize: '16px' }}>Loading positions...</div>
          </div>
        ) : positions && positions.length > 0 ? (
          <div style={{ backgroundColor: '#161b22', borderRadius: '8px', border: '1px solid #30363d', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#0d1117', borderBottom: '2px solid #30363d' }}>
                  <th style={{ textAlign: 'left', padding: '16px', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
                    Symbol
                  </th>
                  <th style={{ textAlign: 'left', padding: '16px', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
                    Strategy
                  </th>
                  <th style={{ textAlign: 'right', padding: '16px', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
                    Shares
                  </th>
                  <th style={{ textAlign: 'right', padding: '16px', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
                    Entry Price
                  </th>
                  <th style={{ textAlign: 'right', padding: '16px', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
                    Stop Loss
                  </th>
                  <th style={{ textAlign: 'right', padding: '16px', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
                    Unrealized P&L
                  </th>
                  <th style={{ textAlign: 'right', padding: '16px', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
                    % Change
                  </th>
                  <th style={{ textAlign: 'center', padding: '16px', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {positions.map((position: Position) => {
                  const isProfitable = position.unrealized_pnl >= 0
                  const isCloseToStopLoss = position.stop_loss &&
                    ((position.entry_price - position.stop_loss) / position.entry_price) * 100 < 1

                  return (
                    <tr key={`${position.strategy_id}-${position.symbol}`} style={{ borderBottom: '1px solid #30363d' }}>
                      <td style={{ padding: '20px 16px' }}>
                        <div style={{ fontWeight: 600, fontSize: '15px', color: '#c9d1d9' }}>{position.symbol}</div>
                        <div style={{ fontSize: '12px', color: '#8b949e', marginTop: '2px' }}>
                          {new Date(position.entry_time).toLocaleString()}
                        </div>
                      </td>
                      <td style={{ padding: '20px 16px' }}>
                        <span style={{
                          padding: '6px 12px',
                          borderRadius: '6px',
                          fontSize: '12px',
                          fontWeight: 600,
                          backgroundColor: '#161b22',
                          color: '#58a6ff',
                          border: '1px solid #30363d',
                          fontFamily: 'monospace'
                        }}>
                          {position.strategy_id.toUpperCase().replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td style={{ padding: '20px 16px', textAlign: 'right', color: '#c9d1d9', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
                        {position.shares.toFixed(2)}
                      </td>
                      <td style={{ padding: '20px 16px', textAlign: 'right', color: '#c9d1d9', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
                        ${position.entry_price.toFixed(2)}
                      </td>
                      <td style={{ padding: '20px 16px', textAlign: 'right' }}>
                        {position.stop_loss ? (
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '6px' }}>
                            {isCloseToStopLoss && (
                              <AlertCircle style={{ width: '14px', height: '14px', color: '#f85149' }} />
                            )}
                            <span style={{ color: '#c9d1d9', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
                              ${position.stop_loss.toFixed(2)}
                            </span>
                          </div>
                        ) : (
                          <span style={{ color: '#8b949e' }}>—</span>
                        )}
                      </td>
                      <td style={{ padding: '20px 16px', textAlign: 'right' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '6px' }}>
                          {isProfitable ? <TrendingUp style={{ width: '16px', height: '16px', color: '#3fb950' }} /> : <TrendingDown style={{ width: '16px', height: '16px', color: '#f85149' }} />}
                          <span style={{ fontSize: '16px', fontWeight: 700, color: isProfitable ? '#3fb950' : '#f85149', fontVariantNumeric: 'tabular-nums' }}>
                            {isProfitable ? '+' : ''}${position.unrealized_pnl.toFixed(2)}
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: '20px 16px', textAlign: 'right' }}>
                        <span style={{
                          fontSize: '14px',
                          fontWeight: 700,
                          color: isProfitable ? '#3fb950' : '#f85149',
                          fontVariantNumeric: 'tabular-nums'
                        }}>
                          {isProfitable ? '+' : ''}{position.unrealized_pnl_percent.toFixed(2)}%
                        </span>
                      </td>
                      <td style={{ padding: '20px 16px', textAlign: 'center' }}>
                        <button
                          onClick={() => closePositionMutation.mutate({ strategy_id: position.strategy_id, symbol: position.symbol })}
                          disabled={closePositionMutation.isPending}
                          style={{
                            padding: '8px 16px',
                            borderRadius: '6px',
                            border: '1px solid #f85149',
                            backgroundColor: 'rgba(248, 81, 73, 0.1)',
                            color: '#f85149',
                            fontSize: '12px',
                            fontWeight: 600,
                            cursor: closePositionMutation.isPending ? 'not-allowed' : 'pointer',
                            opacity: closePositionMutation.isPending ? 0.5 : 1,
                            transition: 'all 0.2s'
                          }}
                          onMouseEnter={(e) => {
                            if (!closePositionMutation.isPending) {
                              e.currentTarget.style.backgroundColor = 'rgba(248, 81, 73, 0.2)'
                            }
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = 'rgba(248, 81, 73, 0.1)'
                          }}
                        >
                          <X style={{ width: '14px', height: '14px', display: 'inline', marginRight: '4px' }} />
                          CLOSE
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '80px 0' }}>
            <Activity style={{ width: '64px', height: '64px', color: '#30363d', margin: '0 auto 16px' }} />
            <div style={{ fontSize: '18px', fontWeight: 600, color: '#c9d1d9', marginBottom: '8px' }}>
              No Open Positions
            </div>
            <div style={{ fontSize: '14px', color: '#8b949e' }}>
              Start a strategy to see automated positions here
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
