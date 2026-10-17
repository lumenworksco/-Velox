import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import EquityChart from '../components/EquityChart'
import WatchlistTable from '../components/WatchlistTable'
import { getPortfolioSummary, getEquityHistory, getPerformanceMetrics } from '../api/portfolio'
import { TrendingUp, TrendingDown } from 'lucide-react'

export default function Dashboard() {
  const [watchlistSymbols, setWatchlistSymbols] = useState(['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'NFLX'])

  const { data: portfolio, isLoading: portfolioLoading } = useQuery({
    queryKey: ['portfolio'],
    queryFn: getPortfolioSummary,
    refetchInterval: 5000,
  })

  const { data: equityHistory } = useQuery({
    queryKey: ['equity-history'],
    queryFn: () => getEquityHistory(30),
  })

  const { data: performance } = useQuery({
    queryKey: ['performance-metrics'],
    queryFn: getPerformanceMetrics,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const dayPnlPositive = (portfolio?.day_pnl ?? 0) >= 0
  const totalPnlPositive = (portfolio?.total_pnl ?? 0) >= 0

  // Calculate equity curve statistics
  const equityStats = equityHistory ? {
    high: Math.max(...equityHistory.map(d => d.equity)),
    low: Math.min(...equityHistory.map(d => d.equity)),
    avg: equityHistory.reduce((sum, d) => sum + d.equity, 0) / equityHistory.length
  } : null

  return (
    <div style={{
      height: '100%',
      width: '100%',
      display: 'grid',
      gridTemplateRows: 'auto 1fr',
      backgroundColor: '#0d1117',
      overflow: 'hidden'
    }}>
      {/* Top Metrics Bar */}
      <div style={{
        backgroundColor: '#161b22',
        borderBottom: '1px solid #30363d',
        padding: '12px 24px'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '32px'
        }}>
          {/* Portfolio Value */}
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
            <div>
              <div style={{ fontSize: '10px', fontFamily: 'monospace', color: '#8b949e', letterSpacing: '0.05em', marginBottom: '2px' }}>PORTFOLIO VALUE</div>
              <div style={{ fontSize: '22px', fontWeight: 700, color: '#c9d1d9', fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.01em' }}>
                {portfolioLoading ? '—' : `$${(portfolio?.total_value ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
              </div>
            </div>
            {!portfolioLoading && portfolio && (
              <div style={{ display: 'flex', alignItems: 'center', fontSize: '13px', fontWeight: 600, color: totalPnlPositive ? '#3fb950' : '#f85149' }}>
                {totalPnlPositive ? <TrendingUp style={{ width: '14px', height: '14px', marginRight: '4px' }} /> : <TrendingDown style={{ width: '14px', height: '14px', marginRight: '4px' }} />}
                {totalPnlPositive ? '+' : ''}{(portfolio.total_pnl_percent).toFixed(2)}%
              </div>
            )}
          </div>

          {/* Day P&L */}
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
            <div>
              <div style={{ fontSize: '10px', fontFamily: 'monospace', color: '#8b949e', letterSpacing: '0.05em', marginBottom: '2px' }}>DAY P&L</div>
              <div style={{ fontSize: '22px', fontWeight: 700, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.01em', color: portfolioLoading ? '#8b949e' : (dayPnlPositive ? '#3fb950' : '#f85149') }}>
                {portfolioLoading ? '—' : `${dayPnlPositive ? '+' : ''}$${Math.abs(portfolio?.day_pnl ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
              </div>
            </div>
            {!portfolioLoading && portfolio && (
              <div style={{ display: 'flex', alignItems: 'center', fontSize: '13px', fontWeight: 600, color: dayPnlPositive ? '#3fb950' : '#f85149' }}>
                {dayPnlPositive ? <TrendingUp style={{ width: '14px', height: '14px', marginRight: '4px' }} /> : <TrendingDown style={{ width: '14px', height: '14px', marginRight: '4px' }} />}
                {dayPnlPositive ? '+' : ''}{(portfolio.day_pnl_percent).toFixed(2)}%
              </div>
            )}
          </div>

          {/* Total P&L */}
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
            <div>
              <div style={{ fontSize: '10px', fontFamily: 'monospace', color: '#8b949e', letterSpacing: '0.05em', marginBottom: '2px' }}>TOTAL P&L</div>
              <div style={{ fontSize: '22px', fontWeight: 700, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.01em', color: portfolioLoading ? '#8b949e' : (totalPnlPositive ? '#3fb950' : '#f85149') }}>
                {portfolioLoading ? '—' : `${totalPnlPositive ? '+' : ''}$${Math.abs(portfolio?.total_pnl ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
              </div>
            </div>
          </div>

          {/* Buying Power */}
          <div>
            <div style={{ fontSize: '10px', fontFamily: 'monospace', color: '#8b949e', letterSpacing: '0.05em', marginBottom: '2px' }}>BUYING POWER</div>
            <div style={{ fontSize: '22px', fontWeight: 700, color: '#c9d1d9', fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.01em' }}>
              {portfolioLoading ? '—' : `$${(portfolio?.buying_power ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '2fr 1fr',
        gridTemplateRows: 'minmax(400px, 1fr) minmax(0, 350px)',
        gap: '1px',
        backgroundColor: '#30363d',
        overflow: 'hidden'
      }}>
        {/* Left Panel - Equity Curve */}
        <div style={{
          gridColumn: '1',
          gridRow: '1',
          backgroundColor: '#0d1117',
          display: 'flex',
          flexDirection: 'column',
          minHeight: 0
        }}>
          <div style={{
            borderBottom: '1px solid #30363d',
            padding: '8px 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <h2 style={{ fontSize: '12px', fontWeight: 700, color: '#c9d1d9', letterSpacing: '0.03em', margin: 0 }}>EQUITY CURVE</h2>
              <span style={{ fontSize: '10px', fontFamily: 'monospace', color: '#8b949e' }}>30D</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '11px', fontFamily: 'monospace' }}>
              <div>
                <span style={{ color: '#8b949e' }}>HIGH</span>
                <span style={{ color: '#3fb950', marginLeft: '8px', fontWeight: 600 }}>
                  {equityStats ? `$${equityStats.high.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—'}
                </span>
              </div>
              <div>
                <span style={{ color: '#8b949e' }}>LOW</span>
                <span style={{ color: '#f85149', marginLeft: '8px', fontWeight: 600 }}>
                  {equityStats ? `$${equityStats.low.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—'}
                </span>
              </div>
              <div>
                <span style={{ color: '#8b949e' }}>AVG</span>
                <span style={{ color: '#c9d1d9', marginLeft: '8px', fontWeight: 600 }}>
                  {equityStats ? `$${equityStats.avg.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—'}
                </span>
              </div>
            </div>
          </div>
          <div style={{ flex: 1, padding: '16px', minHeight: 0 }}>
            <EquityChart data={equityHistory || []} />
          </div>
        </div>

        {/* Right Panel - Performance Stats */}
        <div style={{
          gridColumn: '2',
          gridRow: '1',
          backgroundColor: '#0d1117',
          display: 'flex',
          flexDirection: 'column',
          minHeight: 0
        }}>
          <div style={{
            borderBottom: '1px solid #30363d',
            padding: '8px 16px'
          }}>
            <h2 style={{ fontSize: '12px', fontWeight: 700, color: '#c9d1d9', letterSpacing: '0.03em', margin: 0 }}>PERFORMANCE</h2>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {performance ? (
                performance.total_trades === 0 ? (
                  <div style={{ textAlign: 'center', padding: '32px 0', color: '#8b949e', fontSize: '11px', fontFamily: 'monospace' }}>
                    NO TRADING ACTIVITY
                    <div style={{ marginTop: '8px', fontSize: '10px' }}>
                      Execute trades to see performance metrics
                    </div>
                  </div>
                ) : [
                  { label: 'SHARPE RATIO', value: performance.sharpe_ratio !== 0 ? performance.sharpe_ratio.toFixed(2) : 'N/A', color: '#c9d1d9' },
                  { label: 'MAX DRAWDOWN', value: performance.max_drawdown !== 0 ? `-${performance.max_drawdown.toFixed(2)}%` : 'N/A', color: '#f85149' },
                  { label: 'WIN RATE', value: performance.win_rate !== 0 ? `${performance.win_rate.toFixed(1)}%` : 'N/A', color: performance.win_rate >= 50 ? '#3fb950' : '#8b949e' },
                  { label: 'PROFIT FACTOR', value: performance.profit_factor !== 0 ? performance.profit_factor.toFixed(2) : 'N/A', color: '#c9d1d9' },
                  { label: 'TOTAL TRADES', value: performance.total_trades.toString(), color: '#c9d1d9' },
                  { label: 'AVG WIN', value: performance.avg_win !== 0 ? `+$${performance.avg_win.toFixed(2)}` : 'N/A', color: '#3fb950' },
                  { label: 'AVG LOSS', value: performance.avg_loss !== 0 ? `-$${performance.avg_loss.toFixed(2)}` : 'N/A', color: '#f85149' },
                ].map((stat, idx) => (
                  <div key={stat.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '8px', borderBottom: idx < 6 ? '1px solid #30363d' : 'none' }}>
                    <span style={{ fontSize: '11px', fontFamily: 'monospace', color: '#8b949e' }}>{stat.label}</span>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: stat.color, fontVariantNumeric: 'tabular-nums' }}>{stat.value}</span>
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '32px 0', color: '#8b949e', fontSize: '11px' }}>
                  LOADING METRICS...
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bottom Panel - Watchlist */}
        <div style={{
          gridColumn: '1 / -1',
          gridRow: '2',
          backgroundColor: '#0d1117',
          display: 'flex',
          flexDirection: 'column',
          maxHeight: '400px',
          minHeight: 0
        }}>
          <div style={{
            borderBottom: '1px solid #30363d',
            padding: '8px 16px'
          }}>
            <h2 style={{ fontSize: '12px', fontWeight: 700, color: '#c9d1d9', letterSpacing: '0.03em', margin: 0 }}>WATCHLIST</h2>
          </div>
          <div style={{ flex: 1, overflowY: 'auto' }}>
            <WatchlistTable
              symbols={watchlistSymbols}
              onSymbolsChange={setWatchlistSymbols}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
