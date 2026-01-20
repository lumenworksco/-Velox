import { useQuery } from '@tanstack/react-query'
import { getQuotes } from '../api/market'
import { TrendingUp, TrendingDown, Star, Plus, X } from 'lucide-react'
import { useState } from 'react'

interface WatchlistTableProps {
  symbols: string[]
  onSymbolsChange?: (symbols: string[]) => void
}

export default function WatchlistTable({ symbols, onSymbolsChange }: WatchlistTableProps) {
  const [favorites, setFavorites] = useState<Set<string>>(new Set())
  const [newSymbol, setNewSymbol] = useState('')
  const [showAddInput, setShowAddInput] = useState(false)

  const { data: quotes, isLoading } = useQuery({
    queryKey: ['quotes', symbols],
    queryFn: () => getQuotes(symbols),
    refetchInterval: 2000,
  })

  const toggleFavorite = (symbol: string) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev)
      if (newFavorites.has(symbol)) {
        newFavorites.delete(symbol)
      } else {
        newFavorites.add(symbol)
      }
      return newFavorites
    })
  }

  const removeSymbol = (symbol: string) => {
    if (onSymbolsChange) {
      onSymbolsChange(symbols.filter(s => s !== symbol))
    }
  }

  const addSymbol = () => {
    const upperSymbol = newSymbol.toUpperCase().trim()
    if (upperSymbol && !symbols.includes(upperSymbol)) {
      if (onSymbolsChange) {
        onSymbolsChange([...symbols, upperSymbol])
      }
      setNewSymbol('')
      setShowAddInput(false)
    }
  }

  if (isLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '128px', fontSize: '11px', fontFamily: 'monospace', color: '#8b949e' }}>
        LOADING MARKET DATA...
      </div>
    )
  }

  // Sort quotes to match the input symbols order to prevent switching
  const sortedQuotes = quotes ? [...quotes].sort((a, b) => {
    return symbols.indexOf(a.symbol) - symbols.indexOf(b.symbol)
  }) : []

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', fontSize: '12px', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #30363d', backgroundColor: '#161b22' }}>
            <th style={{ textAlign: 'left', padding: '10px 16px', fontSize: '10px', fontFamily: 'monospace', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                SYMBOL
                <Plus
                  style={{ width: '14px', height: '14px', cursor: 'pointer', color: '#58a6ff' }}
                  onClick={() => setShowAddInput(!showAddInput)}
                />
              </div>
            </th>
            <th style={{ textAlign: 'right', padding: '10px 16px', fontSize: '10px', fontFamily: 'monospace', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
              LAST
            </th>
            <th style={{ textAlign: 'right', padding: '10px 16px', fontSize: '10px', fontFamily: 'monospace', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
              CHG
            </th>
            <th style={{ textAlign: 'right', padding: '10px 16px', fontSize: '10px', fontFamily: 'monospace', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
              CHG %
            </th>
            <th style={{ textAlign: 'right', padding: '10px 16px', fontSize: '10px', fontFamily: 'monospace', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
              HIGH
            </th>
            <th style={{ textAlign: 'right', padding: '10px 16px', fontSize: '10px', fontFamily: 'monospace', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
              LOW
            </th>
            <th style={{ textAlign: 'right', padding: '10px 16px', fontSize: '10px', fontFamily: 'monospace', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700 }}>
              VOLUME
            </th>
            <th style={{ textAlign: 'center', padding: '10px 16px', fontSize: '10px', fontFamily: 'monospace', letterSpacing: '0.05em', color: '#8b949e', fontWeight: 700, width: '50px' }}>

            </th>
          </tr>
        </thead>
        <tbody>
          {showAddInput && (
            <tr style={{ borderBottom: '1px solid #30363d', backgroundColor: '#161b22' }}>
              <td colSpan={8} style={{ padding: '8px 16px' }}>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <input
                    type="text"
                    placeholder="Enter symbol (e.g., TSLA)"
                    value={newSymbol}
                    onChange={(e) => setNewSymbol(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
                    style={{
                      flex: 1,
                      padding: '6px 12px',
                      backgroundColor: '#0d1117',
                      border: '1px solid #30363d',
                      borderRadius: '4px',
                      color: '#c9d1d9',
                      fontSize: '12px',
                      fontFamily: 'monospace'
                    }}
                    autoFocus
                  />
                  <button
                    onClick={addSymbol}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: '#238636',
                      border: 'none',
                      borderRadius: '4px',
                      color: '#fff',
                      fontSize: '11px',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    ADD
                  </button>
                  <button
                    onClick={() => { setShowAddInput(false); setNewSymbol('') }}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: '#21262d',
                      border: '1px solid #30363d',
                      borderRadius: '4px',
                      color: '#8b949e',
                      fontSize: '11px',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    CANCEL
                  </button>
                </div>
              </td>
            </tr>
          )}
          {sortedQuotes.map((quote, idx) => {
            const isPositive = quote.change >= 0

            return (
              <tr
                key={quote.symbol}
                style={{
                  borderBottom: '1px solid rgba(48, 54, 61, 0.5)',
                  backgroundColor: idx % 2 === 0 ? '#0d1117' : '#161b22',
                  transition: 'background-color 0.1s',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#21262d'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = idx % 2 === 0 ? '#0d1117' : '#161b22'}
              >
                <td style={{ padding: '10px 16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Star
                      style={{
                        width: '12px',
                        height: '12px',
                        color: favorites.has(quote.symbol) ? '#f1c232' : '#8b949e',
                        cursor: 'pointer',
                        fill: favorites.has(quote.symbol) ? '#f1c232' : 'none',
                        transition: 'all 0.2s'
                      }}
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleFavorite(quote.symbol)
                      }}
                    />
                    <span style={{ fontWeight: 700, color: '#c9d1d9', letterSpacing: '0.02em' }}>{quote.symbol}</span>
                  </div>
                </td>
                <td style={{ padding: '10px 16px', textAlign: 'right', fontWeight: 700, color: '#c9d1d9', fontVariantNumeric: 'tabular-nums' }}>
                  ${quote.price.toFixed(2)}
                </td>
                <td style={{ padding: '10px 16px', textAlign: 'right', fontWeight: 600, fontVariantNumeric: 'tabular-nums', color: isPositive ? '#3fb950' : '#f85149' }}>
                  {isPositive ? '+' : ''}{quote.change.toFixed(2)}
                </td>
                <td style={{ padding: '10px 16px', textAlign: 'right', fontWeight: 600, fontVariantNumeric: 'tabular-nums', color: isPositive ? '#3fb950' : '#f85149' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                    {isPositive ? (
                      <TrendingUp style={{ width: '12px', height: '12px', marginRight: '4px' }} />
                    ) : (
                      <TrendingDown style={{ width: '12px', height: '12px', marginRight: '4px' }} />
                    )}
                    {isPositive ? '+' : ''}{quote.change_percent.toFixed(2)}%
                  </div>
                </td>
                <td style={{ padding: '10px 16px', textAlign: 'right', color: '#8b949e', fontVariantNumeric: 'tabular-nums', fontFamily: 'monospace' }}>
                  ${(quote.high || quote.price).toFixed(2)}
                </td>
                <td style={{ padding: '10px 16px', textAlign: 'right', color: '#8b949e', fontVariantNumeric: 'tabular-nums', fontFamily: 'monospace' }}>
                  ${(quote.low || quote.price).toFixed(2)}
                </td>
                <td style={{ padding: '10px 16px', textAlign: 'right', color: '#8b949e', fontVariantNumeric: 'tabular-nums', fontFamily: 'monospace', fontSize: '11px' }}>
                  {(quote.volume / 1000000).toFixed(1)}M
                </td>
                <td style={{ padding: '10px 16px', textAlign: 'center' }}>
                  <X
                    style={{
                      width: '14px',
                      height: '14px',
                      color: '#8b949e',
                      cursor: 'pointer',
                      opacity: 0.5,
                      transition: 'opacity 0.2s'
                    }}
                    onClick={(e) => {
                      e.stopPropagation()
                      removeSymbol(quote.symbol)
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.opacity = '1'}
                    onMouseLeave={(e) => e.currentTarget.style.opacity = '0.5'}
                  />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
