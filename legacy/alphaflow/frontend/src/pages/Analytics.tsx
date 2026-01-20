import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Activity, DollarSign, Percent, Target } from 'lucide-react'
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

interface PerformanceMetrics {
  sharpe_ratio: number
  max_drawdown: number
  win_rate: number
  total_trades: number
  avg_win: number
  avg_loss: number
  profit_factor: number
}

interface EquityData {
  date: string
  equity: number
}

interface Position {
  symbol: string
  quantity: number
  avg_price: number
  current_price: number
  unrealized_pnl: number
}

export default function Analytics() {
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null)
  const [equityHistory, setEquityHistory] = useState<EquityData[]>([])
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
    const interval = setInterval(fetchAnalytics, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchAnalytics = async () => {
    try {
      const [perfRes, histRes] = await Promise.all([
        fetch('http://localhost:8000/api/portfolio/performance'),
        fetch('http://localhost:8000/api/portfolio/history')
      ])

      const perfData = await perfRes.json()
      const histData = await histRes.json()

      setPerformance(perfData)
      setEquityHistory(histData)

      // Try to fetch positions if available
      try {
        const posRes = await fetch('http://localhost:8000/api/positions')
        if (posRes.ok) {
          const posData = await posRes.json()
          setPositions(posData)
        }
      } catch (e) {
        console.log('Positions endpoint not available')
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  if (loading) {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#8b949e' }}>Loading analytics...</div>
      </div>
    )
  }

  const totalPnL = positions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0)
  const initialEquity = equityHistory[0]?.equity || 100000
  const currentEquity = equityHistory[equityHistory.length - 1]?.equity || 100000
  const totalReturn = ((currentEquity - initialEquity) / initialEquity) * 100

  return (
    <div style={{ height: '100%', overflow: 'auto', padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#c9d1d9', margin: '0 0 8px 0' }}>
          Performance Analytics
        </h1>
        <p style={{ fontSize: '14px', color: '#8b949e', margin: 0 }}>
          Track your trading performance and key metrics
        </p>
      </div>

      {/* Key Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '16px',
        marginBottom: '32px'
      }}>
        {/* Total Return */}
        <div style={{
          backgroundColor: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', color: '#8b949e', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Total Return
            </span>
            {totalReturn >= 0 ? (
              <TrendingUp size={20} style={{ color: '#3fb950' }} />
            ) : (
              <TrendingDown size={20} style={{ color: '#f85149' }} />
            )}
          </div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: totalReturn >= 0 ? '#3fb950' : '#f85149' }}>
            {totalReturn >= 0 ? '+' : ''}{totalReturn.toFixed(2)}%
          </div>
          <div style={{ fontSize: '13px', color: '#8b949e', marginTop: '8px' }}>
            {formatCurrency(currentEquity - initialEquity)}
          </div>
        </div>

        {/* Sharpe Ratio */}
        <div style={{
          backgroundColor: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', color: '#8b949e', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Sharpe Ratio
            </span>
            <Activity size={20} style={{ color: '#58a6ff' }} />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: '#c9d1d9' }}>
            {performance?.sharpe_ratio.toFixed(2)}
          </div>
          <div style={{ fontSize: '13px', color: '#8b949e', marginTop: '8px' }}>
            Risk-adjusted returns
          </div>
        </div>

        {/* Max Drawdown */}
        <div style={{
          backgroundColor: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', color: '#8b949e', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Max Drawdown
            </span>
            <TrendingDown size={20} style={{ color: '#f85149' }} />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: '#f85149' }}>
            {formatPercent(performance?.max_drawdown || 0)}
          </div>
          <div style={{ fontSize: '13px', color: '#8b949e', marginTop: '8px' }}>
            Peak to trough decline
          </div>
        </div>

        {/* Win Rate */}
        <div style={{
          backgroundColor: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', color: '#8b949e', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Win Rate
            </span>
            <Target size={20} style={{ color: '#3fb950' }} />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: '#c9d1d9' }}>
            {formatPercent(performance?.win_rate || 0)}
          </div>
          <div style={{ fontSize: '13px', color: '#8b949e', marginTop: '8px' }}>
            {performance?.total_trades || 0} total trades
          </div>
        </div>

        {/* Profit Factor */}
        <div style={{
          backgroundColor: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', color: '#8b949e', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Profit Factor
            </span>
            <Percent size={20} style={{ color: '#58a6ff' }} />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: '#c9d1d9' }}>
            {performance?.profit_factor.toFixed(2)}
          </div>
          <div style={{ fontSize: '13px', color: '#8b949e', marginTop: '8px' }}>
            Gross profit / gross loss
          </div>
        </div>

        {/* Average Win */}
        <div style={{
          backgroundColor: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', color: '#8b949e', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Avg Win / Loss
            </span>
            <DollarSign size={20} style={{ color: '#58a6ff' }} />
          </div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#3fb950' }}>
            {formatCurrency(performance?.avg_win || 0)}
          </div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#f85149', marginTop: '4px' }}>
            {formatCurrency(performance?.avg_loss || 0)}
          </div>
        </div>
      </div>

      {/* Equity Curve */}
      <div style={{
        backgroundColor: '#161b22',
        border: '1px solid #30363d',
        borderRadius: '8px',
        padding: '24px',
        marginBottom: '32px'
      }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#c9d1d9', margin: '0 0 24px 0' }}>
          Equity Curve
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={equityHistory}>
            <defs>
              <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#58a6ff" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#58a6ff" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              stroke="#8b949e"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              stroke="#8b949e"
              style={{ fontSize: '12px' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#161b22',
                border: '1px solid #30363d',
                borderRadius: '6px',
                fontSize: '12px'
              }}
              labelFormatter={(label) => new Date(label).toLocaleDateString()}
              formatter={(value: number) => [formatCurrency(value), 'Equity']}
            />
            <Area
              type="monotone"
              dataKey="equity"
              stroke="#58a6ff"
              strokeWidth={2}
              fill="url(#equityGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Position Performance */}
      {positions.length > 0 && (
        <div style={{
          backgroundColor: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '24px'
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#c9d1d9', margin: '0 0 24px 0' }}>
            Position Performance
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={positions}>
              <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
              <XAxis
                dataKey="symbol"
                stroke="#8b949e"
                style={{ fontSize: '12px' }}
              />
              <YAxis
                tickFormatter={(value) => formatCurrency(value)}
                stroke="#8b949e"
                style={{ fontSize: '12px' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#161b22',
                  border: '1px solid #30363d',
                  borderRadius: '6px',
                  fontSize: '12px'
                }}
                formatter={(value: number) => [formatCurrency(value), 'P&L']}
              />
              <Bar
                dataKey="unrealized_pnl"
                fill="#58a6ff"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
