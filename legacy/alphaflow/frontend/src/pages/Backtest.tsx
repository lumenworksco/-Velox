import { useState, useEffect } from 'react'
import { Play, StopCircle, TrendingUp, TrendingDown, Activity, Target, Clock, DollarSign } from 'lucide-react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface BacktestConfig {
  symbols: string[]
  strategy: string
  startDate: string
  endDate: string
  initialCapital: number
  commission: number
}

interface BacktestStatus {
  backtest_id: string
  status: string
  progress: number
  message: string
}

interface BacktestResult {
  backtest_id: string
  total_return: number
  sharpe_ratio: number
  max_drawdown: number
  win_rate: number
  total_trades: number
  final_equity: number
  execution_time: number
}

interface Strategy {
  id: string
  name: string
  description: string
}

const strategies: Strategy[] = [
  { id: 'multi_timeframe', name: '🚀 Multi-Timeframe Confluence', description: 'ADVANCED: Analyzes daily, hourly, and intraday timeframes' },
  { id: 'volatility_breakout', name: '⚡ Volatility Breakout', description: 'ADVANCED: ATR-based breakout strategy with volume confirmation' },
  { id: 'ma_crossover', name: 'Moving Average Crossover', description: 'Buy when fast MA crosses above slow MA' },
  { id: 'rsi_mean_reversion', name: 'RSI Mean Reversion', description: 'Buy oversold, sell overbought based on RSI' },
  { id: 'momentum', name: 'Momentum Strategy', description: 'Follow strong price trends' },
  { id: 'mean_reversion', name: 'Mean Reversion', description: 'Fade extreme moves back to the mean' },
  { id: 'quick_test', name: 'Quick Test Strategy', description: 'Fast executing test strategy with 1-minute bars' }
]

export default function Backtest() {
  const [config, setConfig] = useState<BacktestConfig>({
    symbols: ['AAPL'],
    strategy: 'ma_crossover',
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    initialCapital: 100000,
    commission: 0.001
  })

  const [running, setRunning] = useState(false)
  const [currentBacktestId, setCurrentBacktestId] = useState<string | null>(null)
  const [status, setStatus] = useState<BacktestStatus | null>(null)
  const [result, setResult] = useState<BacktestResult | null>(null)
  const [symbolInput, setSymbolInput] = useState('AAPL')
  const [symbolError, setSymbolError] = useState<string | null>(null)
  const [validatingSymbol, setValidatingSymbol] = useState(false)

  useEffect(() => {
    if (currentBacktestId && running) {
      const interval = setInterval(checkStatus, 1000)
      return () => clearInterval(interval)
    }
  }, [currentBacktestId, running])

  const checkStatus = async () => {
    if (!currentBacktestId) return

    try {
      const res = await fetch(`http://localhost:8000/api/backtest/status/${currentBacktestId}`)
      const statusData = await res.json()
      setStatus(statusData)

      if (statusData.status === 'completed') {
        const resultRes = await fetch(`http://localhost:8000/api/backtest/results/${currentBacktestId}`)
        const resultData = await resultRes.json()
        setResult(resultData)
        setRunning(false)
      } else if (statusData.status === 'failed') {
        setRunning(false)
        setResult(null)
      }
    } catch (error) {
      console.error('Failed to check backtest status:', error)
      setRunning(false)
    }
  }

  const runBacktest = async () => {
    try {
      setRunning(true)
      setResult(null)
      setStatus(null)

      const res = await fetch('http://localhost:8000/api/backtest/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbols: config.symbols,
          strategy: config.strategy,
          start_date: config.startDate,
          end_date: config.endDate,
          initial_capital: config.initialCapital,
          commission: config.commission
        })
      })

      const data = await res.json()
      setCurrentBacktestId(data.backtest_id)
      setStatus(data)
    } catch (error) {
      console.error('Failed to start backtest:', error)
      setRunning(false)
    }
  }

  const stopBacktest = async () => {
    if (!currentBacktestId) return

    try {
      await fetch(`http://localhost:8000/api/backtest/${currentBacktestId}`, {
        method: 'DELETE'
      })
      setRunning(false)
      setStatus(null)
    } catch (error) {
      console.error('Failed to stop backtest:', error)
    }
  }

  const addSymbol = async () => {
    const symbol = symbolInput.trim().toUpperCase()

    if (!symbol) {
      setSymbolError('Please enter a symbol')
      return
    }

    if (config.symbols.includes(symbol)) {
      setSymbolError('Symbol already added')
      return
    }

    // Validate symbol by checking if we can get quote data
    setValidatingSymbol(true)
    setSymbolError(null)

    try {
      const response = await fetch(`http://localhost:8000/api/market/quote/${symbol}`)

      if (!response.ok) {
        setSymbolError(`Invalid symbol: ${symbol}`)
        setValidatingSymbol(false)
        return
      }

      const data = await response.json()

      // Check if we got valid data
      if (!data || !data.price || data.price === 0) {
        setSymbolError(`No data available for: ${symbol}`)
        setValidatingSymbol(false)
        return
      }

      // Symbol is valid, add it
      setConfig({ ...config, symbols: [...config.symbols, symbol] })
      setSymbolInput('')
      setSymbolError(null)
    } catch (error) {
      setSymbolError(`Failed to validate symbol: ${symbol}`)
    } finally {
      setValidatingSymbol(false)
    }
  }

  const removeSymbol = (symbol: string) => {
    setConfig({ ...config, symbols: config.symbols.filter(s => s !== symbol) })
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

  return (
    <div style={{ height: '100%', overflow: 'auto', padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#c9d1d9', margin: '0 0 8px 0' }}>
          Strategy Backtesting
        </h1>
        <p style={{ fontSize: '14px', color: '#8b949e', margin: 0 }}>
          Test your trading strategies against historical data
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '400px 1fr', gap: '24px' }}>
        {/* Configuration Panel */}
        <div style={{
          backgroundColor: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '24px',
          height: 'fit-content'
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#c9d1d9', margin: '0 0 24px 0' }}>
            Configuration
          </h2>

          {/* Strategy Selection */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '13px', color: '#8b949e', marginBottom: '8px' }}>
              Strategy
            </label>
            <select
              value={config.strategy}
              onChange={(e) => setConfig({ ...config, strategy: e.target.value })}
              disabled={running}
              style={{
                width: '100%',
                padding: '10px 12px',
                backgroundColor: '#0d1117',
                border: '1px solid #30363d',
                borderRadius: '6px',
                color: '#c9d1d9',
                fontSize: '14px'
              }}
            >
              {strategies.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
            <p style={{ fontSize: '12px', color: '#8b949e', margin: '8px 0 0 0' }}>
              {strategies.find(s => s.id === config.strategy)?.description}
            </p>
          </div>

          {/* Symbols */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '13px', color: '#8b949e', marginBottom: '8px' }}>
              Symbols
            </label>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
              <input
                type="text"
                value={symbolInput}
                onChange={(e) => {
                  setSymbolInput(e.target.value)
                  setSymbolError(null)
                }}
                onKeyPress={(e) => e.key === 'Enter' && !validatingSymbol && addSymbol()}
                placeholder="Add symbol (e.g. AAPL)"
                disabled={running || validatingSymbol}
                style={{
                  flex: 1,
                  padding: '10px 12px',
                  backgroundColor: '#0d1117',
                  border: `1px solid ${symbolError ? '#f85149' : '#30363d'}`,
                  borderRadius: '6px',
                  color: '#c9d1d9',
                  fontSize: '14px'
                }}
              />
              <button
                onClick={addSymbol}
                disabled={running || validatingSymbol}
                style={{
                  padding: '10px 16px',
                  backgroundColor: validatingSymbol ? '#8b949e' : '#238636',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '14px',
                  cursor: running || validatingSymbol ? 'not-allowed' : 'pointer',
                  opacity: running || validatingSymbol ? 0.5 : 1
                }}
              >
                {validatingSymbol ? 'Checking...' : 'Add'}
              </button>
            </div>
            {symbolError && (
              <p style={{ fontSize: '12px', color: '#f85149', margin: '4px 0 8px 0' }}>
                {symbolError}
              </p>
            )}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {config.symbols.map(symbol => (
                <div
                  key={symbol}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '6px 12px',
                    backgroundColor: '#0d1117',
                    border: '1px solid #30363d',
                    borderRadius: '6px',
                    fontSize: '13px',
                    color: '#c9d1d9'
                  }}
                >
                  {symbol}
                  {!running && (
                    <button
                      onClick={() => removeSymbol(symbol)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#8b949e',
                        cursor: 'pointer',
                        padding: 0,
                        fontSize: '16px'
                      }}
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Date Range */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '13px', color: '#8b949e', marginBottom: '8px' }}>
              Start Date
            </label>
            <input
              type="date"
              value={config.startDate}
              onChange={(e) => setConfig({ ...config, startDate: e.target.value })}
              disabled={running}
              style={{
                width: '100%',
                padding: '10px 12px',
                backgroundColor: '#0d1117',
                border: '1px solid #30363d',
                borderRadius: '6px',
                color: '#c9d1d9',
                fontSize: '14px'
              }}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '13px', color: '#8b949e', marginBottom: '8px' }}>
              End Date
            </label>
            <input
              type="date"
              value={config.endDate}
              onChange={(e) => setConfig({ ...config, endDate: e.target.value })}
              disabled={running}
              style={{
                width: '100%',
                padding: '10px 12px',
                backgroundColor: '#0d1117',
                border: '1px solid #30363d',
                borderRadius: '6px',
                color: '#c9d1d9',
                fontSize: '14px'
              }}
            />
          </div>

          {/* Initial Capital */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '13px', color: '#8b949e', marginBottom: '8px' }}>
              Initial Capital
            </label>
            <input
              type="number"
              value={config.initialCapital}
              onChange={(e) => setConfig({ ...config, initialCapital: Number(e.target.value) })}
              disabled={running}
              style={{
                width: '100%',
                padding: '10px 12px',
                backgroundColor: '#0d1117',
                border: '1px solid #30363d',
                borderRadius: '6px',
                color: '#c9d1d9',
                fontSize: '14px'
              }}
            />
          </div>

          {/* Commission */}
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '13px', color: '#8b949e', marginBottom: '8px' }}>
              Commission (%)
            </label>
            <input
              type="number"
              step="0.001"
              value={config.commission * 100}
              onChange={(e) => setConfig({ ...config, commission: Number(e.target.value) / 100 })}
              disabled={running}
              style={{
                width: '100%',
                padding: '10px 12px',
                backgroundColor: '#0d1117',
                border: '1px solid #30363d',
                borderRadius: '6px',
                color: '#c9d1d9',
                fontSize: '14px'
              }}
            />
          </div>

          {/* Run Button */}
          {!running ? (
            <button
              onClick={runBacktest}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: '#238636',
                border: 'none',
                borderRadius: '6px',
                color: '#fff',
                fontSize: '14px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              <Play size={16} />
              Run Backtest
            </button>
          ) : (
            <button
              onClick={stopBacktest}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: '#da3633',
                border: 'none',
                borderRadius: '6px',
                color: '#fff',
                fontSize: '14px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              <StopCircle size={16} />
              Stop Backtest
            </button>
          )}
        </div>

        {/* Results Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Status */}
          {status && (
            <div style={{
              backgroundColor: '#161b22',
              border: `1px solid ${status.status === 'failed' ? '#f85149' : '#30363d'}`,
              borderRadius: '8px',
              padding: '24px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                <h2 style={{
                  fontSize: '18px',
                  fontWeight: 600,
                  color: status.status === 'failed' ? '#f85149' : '#c9d1d9',
                  margin: 0
                }}>
                  {status.status === 'completed' ? 'Backtest Completed' :
                   status.status === 'failed' ? 'Backtest Failed' :
                   'Running Backtest...'}
                </h2>
                {status.status !== 'failed' && (
                  <span style={{ fontSize: '14px', color: '#8b949e' }}>{status.progress}%</span>
                )}
              </div>
              {status.status !== 'failed' && (
                <div style={{
                  width: '100%',
                  height: '8px',
                  backgroundColor: '#0d1117',
                  borderRadius: '4px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${status.progress}%`,
                    height: '100%',
                    backgroundColor: '#238636',
                    transition: 'width 0.3s ease'
                  }} />
                </div>
              )}
              <p style={{
                fontSize: '13px',
                color: status.status === 'failed' ? '#f85149' : '#8b949e',
                margin: '12px 0 0 0'
              }}>
                {status.message}
              </p>
            </div>
          )}

          {/* Results */}
          {result && (
            <>
              {/* Metrics Grid */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '16px'
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
                    {result.total_return >= 0 ? (
                      <TrendingUp size={20} style={{ color: '#3fb950' }} />
                    ) : (
                      <TrendingDown size={20} style={{ color: '#f85149' }} />
                    )}
                  </div>
                  <div style={{ fontSize: '28px', fontWeight: 700, color: result.total_return >= 0 ? '#3fb950' : '#f85149' }}>
                    {result.total_return >= 0 ? '+' : ''}{formatPercent(result.total_return)}
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
                  <div style={{ fontSize: '28px', fontWeight: 700, color: '#c9d1d9' }}>
                    {result.sharpe_ratio.toFixed(2)}
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
                  <div style={{ fontSize: '28px', fontWeight: 700, color: '#f85149' }}>
                    {formatPercent(result.max_drawdown)}
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
                  <div style={{ fontSize: '28px', fontWeight: 700, color: '#c9d1d9' }}>
                    {formatPercent(result.win_rate)}
                  </div>
                  <div style={{ fontSize: '13px', color: '#8b949e', marginTop: '8px' }}>
                    {result.total_trades} trades
                  </div>
                </div>

                {/* Final Equity */}
                <div style={{
                  backgroundColor: '#161b22',
                  border: '1px solid #30363d',
                  borderRadius: '8px',
                  padding: '20px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontSize: '13px', color: '#8b949e', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Final Equity
                    </span>
                    <DollarSign size={20} style={{ color: '#58a6ff' }} />
                  </div>
                  <div style={{ fontSize: '28px', fontWeight: 700, color: '#c9d1d9' }}>
                    {formatCurrency(result.final_equity)}
                  </div>
                </div>

                {/* Execution Time */}
                <div style={{
                  backgroundColor: '#161b22',
                  border: '1px solid #30363d',
                  borderRadius: '8px',
                  padding: '20px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ fontSize: '13px', color: '#8b949e', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Execution Time
                    </span>
                    <Clock size={20} style={{ color: '#8b949e' }} />
                  </div>
                  <div style={{ fontSize: '28px', fontWeight: 700, color: '#c9d1d9' }}>
                    {result.execution_time.toFixed(2)}s
                  </div>
                </div>
              </div>
            </>
          )}

          {/* Empty State */}
          {!status && !result && (
            <div style={{
              backgroundColor: '#161b22',
              border: '1px solid #30363d',
              borderRadius: '8px',
              padding: '80px 24px',
              textAlign: 'center'
            }}>
              <Activity size={48} style={{ color: '#8b949e', margin: '0 auto 16px' }} />
              <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#c9d1d9', margin: '0 0 8px 0' }}>
                Ready to Backtest
              </h3>
              <p style={{ fontSize: '14px', color: '#8b949e', margin: 0 }}>
                Configure your backtest parameters and click "Run Backtest" to begin
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
