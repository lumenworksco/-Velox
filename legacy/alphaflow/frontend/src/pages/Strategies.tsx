import { useState, useEffect } from 'react'
import { Play, Square, TrendingUp, Settings, BarChart3, Clock, DollarSign } from 'lucide-react'

interface Strategy {
  id: string
  name: string
  description: string
  status: string
  symbols: string[]
  parameters: Record<string, number>
}

interface StrategyPerformance {
  strategy_id: string
  total_pnl: number
  total_trades: number
  win_rate: number
  sharpe_ratio: number
}

export default function Strategies() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [performances, setPerformances] = useState<Record<string, StrategyPerformance>>({})
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null)
  const [editedParams, setEditedParams] = useState<Record<string, number>>({})
  const [editedSymbols, setEditedSymbols] = useState<string[]>([])
  const [newSymbol, setNewSymbol] = useState('')
  const [symbolError, setSymbolError] = useState('')
  const [saveError, setSaveError] = useState('')

  useEffect(() => {
    fetchStrategies()
    const interval = setInterval(fetchStrategies, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchStrategies = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/strategies/list')
      const data = await res.json()
      setStrategies(data)

      // Fetch performance for each strategy
      const perfPromises = data.map(async (strategy: Strategy) => {
        try {
          const perfRes = await fetch(`http://localhost:8000/api/strategies/${strategy.id}/performance`)
          const perfData = await perfRes.json()
          return { id: strategy.id, data: perfData }
        } catch {
          return null
        }
      })

      const perfResults = await Promise.all(perfPromises)
      const perfMap: Record<string, StrategyPerformance> = {}
      perfResults.forEach(result => {
        if (result) {
          perfMap[result.id] = result.data
        }
      })
      setPerformances(perfMap)
    } catch (error) {
      console.error('Failed to fetch strategies:', error)
    } finally {
      setLoading(false)
    }
  }

  const startStrategy = async (strategyId: string) => {
    setActionLoading(strategyId)
    try {
      await fetch(`http://localhost:8000/api/strategies/${strategyId}/start`, {
        method: 'POST'
      })
      await fetchStrategies()
    } catch (error) {
      console.error('Failed to start strategy:', error)
    } finally {
      setActionLoading(null)
    }
  }

  const stopStrategy = async (strategyId: string) => {
    setActionLoading(strategyId)
    try {
      await fetch(`http://localhost:8000/api/strategies/${strategyId}/stop`, {
        method: 'POST'
      })
      await fetchStrategies()
    } catch (error) {
      console.error('Failed to stop strategy:', error)
    } finally {
      setActionLoading(null)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#3fb950'
      case 'paused': return '#d29922'
      default: return '#8b949e'
    }
  }

  const getStatusLabel = (status: string) => {
    return status.charAt(0).toUpperCase() + status.slice(1)
  }

  const openSettings = (strategy: Strategy) => {
    setEditingStrategy(strategy)
    setEditedParams({ ...strategy.parameters })
    setEditedSymbols([...strategy.symbols])
    setNewSymbol('')
    setSaveError('')  // Clear any previous save errors
  }

  const closeSettings = () => {
    setEditingStrategy(null)
    setEditedParams({})
    setEditedSymbols([])
    setNewSymbol('')
    setSaveError('')  // Clear save errors when closing
  }

  const addSymbol = () => {
    const symbol = newSymbol.trim().toUpperCase()

    // Clear previous error
    setSymbolError('')

    // Validate format
    if (!symbol) {
      setSymbolError('Please enter a symbol')
      return
    }

    if (symbol.length > 5) {
      setSymbolError('Symbol too long (max 5 characters)')
      return
    }

    if (!/^[A-Z]+$/.test(symbol)) {
      setSymbolError('Symbol must contain only letters')
      return
    }

    if (editedSymbols.includes(symbol)) {
      setSymbolError('Symbol already added')
      return
    }

    // Add symbol (backend will validate if it's real)
    setEditedSymbols([...editedSymbols, symbol])
    setNewSymbol('')
  }

  const removeSymbol = (symbolToRemove: string) => {
    setEditedSymbols(editedSymbols.filter(s => s !== symbolToRemove))
  }

  const saveSettings = async () => {
    if (!editingStrategy) return

    // Clear previous errors
    setSaveError('')

    try {
      // Save parameters to backend
      const paramsResponse = await fetch(
        `http://localhost:8000/api/strategies/${editingStrategy.id}/parameters`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(editedParams)
        }
      )

      if (!paramsResponse.ok) {
        const error = await paramsResponse.json()
        setSaveError(error.detail || 'Failed to save parameters')
        return  // Don't close modal, let user see the error
      }

      // Save symbols to backend
      const symbolsResponse = await fetch(
        `http://localhost:8000/api/strategies/${editingStrategy.id}/symbols`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(editedSymbols)
        }
      )

      if (!symbolsResponse.ok) {
        const error = await symbolsResponse.json()
        setSaveError(error.detail || 'Failed to save symbols')
        return  // Don't close modal, let user see the error
      }

      // Update local state
      const updatedStrategies = strategies.map(s =>
        s.id === editingStrategy.id
          ? { ...s, parameters: editedParams, symbols: editedSymbols }
          : s
      )
      setStrategies(updatedStrategies)
      closeSettings()
    } catch (error) {
      console.error('Failed to save settings:', error)
      setSaveError(error instanceof Error ? error.message : 'Failed to save settings')
    }
  }

  const updateParameter = (key: string, value: string) => {
    const numValue = parseFloat(value)
    if (!isNaN(numValue)) {
      setEditedParams({ ...editedParams, [key]: numValue })
    }
  }

  if (loading) {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#8b949e' }}>Loading strategies...</div>
      </div>
    )
  }

  return (
    <div style={{ height: '100%', overflow: 'auto', padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#c9d1d9', margin: '0 0 8px 0' }}>
          Trading Strategies
        </h1>
        <p style={{ fontSize: '14px', color: '#8b949e', margin: 0 }}>
          Manage and monitor your algorithmic trading strategies
        </p>
      </div>

      {/* Strategy Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(450px, 1fr))', gap: '24px' }}>
        {strategies.map(strategy => {
          const perf = performances[strategy.id]
          const isActive = strategy.status === 'active'
          const isLoading = actionLoading === strategy.id

          return (
            <div
              key={strategy.id}
              style={{
                backgroundColor: '#161b22',
                border: `1px solid ${isActive ? getStatusColor('active') : '#30363d'}`,
                borderRadius: '8px',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px'
              }}
            >
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                    <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#c9d1d9', margin: 0 }}>
                      {strategy.name}
                    </h3>
                    <div style={{
                      padding: '4px 8px',
                      backgroundColor: `${getStatusColor(strategy.status)}20`,
                      border: `1px solid ${getStatusColor(strategy.status)}`,
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 600,
                      color: getStatusColor(strategy.status),
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      {getStatusLabel(strategy.status)}
                    </div>
                  </div>
                  <p style={{ fontSize: '13px', color: '#8b949e', margin: 0 }}>
                    {strategy.description}
                  </p>
                </div>
              </div>

              {/* Symbols */}
              <div>
                <div style={{ fontSize: '12px', color: '#8b949e', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Trading Symbols
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {strategy.symbols.map(symbol => (
                    <div
                      key={symbol}
                      style={{
                        padding: '4px 10px',
                        backgroundColor: '#0d1117',
                        border: '1px solid #30363d',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 600,
                        color: '#c9d1d9'
                      }}
                    >
                      {symbol}
                    </div>
                  ))}
                </div>
              </div>

              {/* Parameters */}
              <div>
                <div style={{ fontSize: '12px', color: '#8b949e', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Parameters
                </div>
                <div style={{
                  backgroundColor: '#0d1117',
                  border: '1px solid #30363d',
                  borderRadius: '6px',
                  padding: '12px'
                }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                    {Object.entries(strategy.parameters).map(([key, value]) => (
                      <div key={key} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                        <span style={{ color: '#8b949e' }}>
                          {key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}:
                        </span>
                        <span style={{ color: '#c9d1d9', fontWeight: 600 }}>{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Performance Metrics */}
              {perf && (
                <div>
                  <div style={{ fontSize: '12px', color: '#8b949e', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    Performance
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                    {/* Total P&L */}
                    <div style={{
                      backgroundColor: '#0d1117',
                      border: '1px solid #30363d',
                      borderRadius: '6px',
                      padding: '12px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <DollarSign size={14} style={{ color: '#58a6ff' }} />
                        <span style={{ fontSize: '11px', color: '#8b949e' }}>Total P&L</span>
                      </div>
                      <div style={{
                        fontSize: '18px',
                        fontWeight: 700,
                        color: perf.total_pnl >= 0 ? '#3fb950' : '#f85149'
                      }}>
                        {formatCurrency(perf.total_pnl)}
                      </div>
                    </div>

                    {/* Win Rate */}
                    <div style={{
                      backgroundColor: '#0d1117',
                      border: '1px solid #30363d',
                      borderRadius: '6px',
                      padding: '12px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <TrendingUp size={14} style={{ color: '#58a6ff' }} />
                        <span style={{ fontSize: '11px', color: '#8b949e' }}>Win Rate</span>
                      </div>
                      <div style={{ fontSize: '18px', fontWeight: 700, color: '#c9d1d9' }}>
                        {perf.win_rate.toFixed(1)}%
                      </div>
                    </div>

                    {/* Total Trades */}
                    <div style={{
                      backgroundColor: '#0d1117',
                      border: '1px solid #30363d',
                      borderRadius: '6px',
                      padding: '12px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <BarChart3 size={14} style={{ color: '#58a6ff' }} />
                        <span style={{ fontSize: '11px', color: '#8b949e' }}>Total Trades</span>
                      </div>
                      <div style={{ fontSize: '18px', fontWeight: 700, color: '#c9d1d9' }}>
                        {perf.total_trades}
                      </div>
                    </div>

                    {/* Sharpe Ratio */}
                    <div style={{
                      backgroundColor: '#0d1117',
                      border: '1px solid #30363d',
                      borderRadius: '6px',
                      padding: '12px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <Clock size={14} style={{ color: '#58a6ff' }} />
                        <span style={{ fontSize: '11px', color: '#8b949e' }}>Sharpe Ratio</span>
                      </div>
                      <div style={{ fontSize: '18px', fontWeight: 700, color: '#c9d1d9' }}>
                        {perf.sharpe_ratio.toFixed(2)}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div style={{ display: 'flex', gap: '8px', paddingTop: '8px', borderTop: '1px solid #30363d' }}>
                {!isActive ? (
                  <button
                    onClick={() => startStrategy(strategy.id)}
                    disabled={isLoading}
                    style={{
                      flex: 1,
                      padding: '10px',
                      backgroundColor: '#238636',
                      border: 'none',
                      borderRadius: '6px',
                      color: '#fff',
                      fontSize: '14px',
                      fontWeight: 600,
                      cursor: isLoading ? 'not-allowed' : 'pointer',
                      opacity: isLoading ? 0.5 : 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px'
                    }}
                  >
                    <Play size={16} />
                    {isLoading ? 'Starting...' : 'Start Strategy'}
                  </button>
                ) : (
                  <button
                    onClick={() => stopStrategy(strategy.id)}
                    disabled={isLoading}
                    style={{
                      flex: 1,
                      padding: '10px',
                      backgroundColor: '#da3633',
                      border: 'none',
                      borderRadius: '6px',
                      color: '#fff',
                      fontSize: '14px',
                      fontWeight: 600,
                      cursor: isLoading ? 'not-allowed' : 'pointer',
                      opacity: isLoading ? 0.5 : 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px'
                    }}
                  >
                    <Square size={16} />
                    {isLoading ? 'Stopping...' : 'Stop Strategy'}
                  </button>
                )}
                <button
                  onClick={() => openSettings(strategy)}
                  style={{
                    padding: '10px 16px',
                    backgroundColor: '#0d1117',
                    border: '1px solid #30363d',
                    borderRadius: '6px',
                    color: '#8b949e',
                    fontSize: '14px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#58a6ff'
                    e.currentTarget.style.color = '#58a6ff'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#30363d'
                    e.currentTarget.style.color = '#8b949e'
                  }}
                >
                  <Settings size={16} />
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Empty State */}
      {strategies.length === 0 && (
        <div style={{
          backgroundColor: '#161b22',
          border: '1px solid #30363d',
          borderRadius: '8px',
          padding: '80px 24px',
          textAlign: 'center'
        }}>
          <TrendingUp size={48} style={{ color: '#8b949e', margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#c9d1d9', margin: '0 0 8px 0' }}>
            No Strategies Available
          </h3>
          <p style={{ fontSize: '14px', color: '#8b949e', margin: 0 }}>
            Create your first trading strategy to get started
          </p>
        </div>
      )}

      {/* Settings Modal */}
      {editingStrategy && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={closeSettings}
        >
          <div
            style={{
              backgroundColor: '#161b22',
              border: '1px solid #30363d',
              borderRadius: '8px',
              padding: '24px',
              width: '500px',
              maxWidth: '90%'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#c9d1d9', margin: '0 0 8px 0' }}>
                {editingStrategy.name} Settings
              </h2>
              <p style={{ fontSize: '13px', color: '#8b949e', margin: 0 }}>
                Adjust strategy parameters
              </p>
            </div>

            {/* Symbols */}
            <div style={{ marginBottom: '24px' }}>
              <div style={{ fontSize: '12px', color: '#8b949e', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Trading Symbols
              </div>
              <div style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '8px' }}>
                  {editedSymbols.map(symbol => (
                    <div
                      key={symbol}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '4px 8px',
                        backgroundColor: '#0d1117',
                        border: '1px solid #30363d',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 600,
                        color: '#c9d1d9'
                      }}
                    >
                      {symbol}
                      <button
                        onClick={() => removeSymbol(symbol)}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#da3633',
                          cursor: 'pointer',
                          padding: '0 2px',
                          fontSize: '14px',
                          lineHeight: 1
                        }}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
                <div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input
                      type="text"
                      value={newSymbol}
                      onChange={(e) => {
                        setNewSymbol(e.target.value.toUpperCase())
                        setSymbolError('')  // Clear error on input
                      }}
                      onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
                      placeholder="Add symbol (e.g., AAPL)"
                      style={{
                        flex: 1,
                        padding: '8px 12px',
                        backgroundColor: '#0d1117',
                        border: `1px solid ${symbolError ? '#da3633' : '#30363d'}`,
                        borderRadius: '6px',
                        color: '#c9d1d9',
                        fontSize: '14px',
                        outline: 'none'
                      }}
                    />
                    <button
                      onClick={addSymbol}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#238636',
                        border: 'none',
                        borderRadius: '6px',
                        color: '#fff',
                        fontSize: '14px',
                        fontWeight: 600,
                        cursor: 'pointer'
                      }}
                    >
                      Add
                    </button>
                  </div>
                  {symbolError && (
                    <div style={{
                      marginTop: '6px',
                      fontSize: '12px',
                      color: '#f85149'
                    }}>
                      {symbolError}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Parameters */}
            <div style={{ marginBottom: '24px' }}>
              <div style={{ fontSize: '12px', color: '#8b949e', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Parameters
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {Object.entries(editedParams).map(([key, value]) => (
                  <div key={key}>
                    <label
                      htmlFor={`param-${key}`}
                      style={{
                        display: 'block',
                        fontSize: '13px',
                        color: '#c9d1d9',
                        marginBottom: '6px',
                        fontWeight: 500
                      }}
                    >
                      {key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </label>
                    <input
                      id={`param-${key}`}
                      type="number"
                      value={value}
                      onChange={(e) => updateParameter(key, e.target.value)}
                      step="any"
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        backgroundColor: '#0d1117',
                        border: '1px solid #30363d',
                        borderRadius: '6px',
                        color: '#c9d1d9',
                        fontSize: '14px',
                        outline: 'none',
                        transition: 'border-color 0.2s'
                      }}
                      onFocus={(e) => e.target.style.borderColor = '#58a6ff'}
                      onBlur={(e) => e.target.style.borderColor = '#30363d'}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Error Banner */}
            {saveError && (
              <div style={{
                padding: '12px 16px',
                backgroundColor: 'rgba(248, 81, 73, 0.1)',
                border: '1px solid #da3633',
                borderRadius: '6px',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px'
              }}>
                <div style={{
                  fontSize: '16px',
                  lineHeight: 1,
                  color: '#f85149',
                  marginTop: '2px'
                }}>
                  ⚠
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontSize: '13px',
                    fontWeight: 600,
                    color: '#f85149',
                    marginBottom: '4px'
                  }}>
                    Validation Error
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: '#ffa198',
                    lineHeight: 1.5
                  }}>
                    {saveError}
                  </div>
                </div>
              </div>
            )}

            {/* Actions */}
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button
                onClick={closeSettings}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#0d1117',
                  border: '1px solid #30363d',
                  borderRadius: '6px',
                  color: '#c9d1d9',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = '#58a6ff'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = '#30363d'}
              >
                Cancel
              </button>
              <button
                onClick={saveSettings}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#238636',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2ea043'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#238636'}
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
