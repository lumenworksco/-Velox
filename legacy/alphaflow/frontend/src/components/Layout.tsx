import { ReactNode, useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  LayoutDashboard,
  TrendingUp,
  BarChart3,
  TestTube2,
  Sparkles,
  Activity,
  Settings,
  AlertTriangle,
  Zap
} from 'lucide-react'
import { getQuotes } from '../api/market'

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Trading', path: '/trading', icon: TrendingUp },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  { name: 'Backtest', path: '/backtest', icon: TestTube2 },
  { name: 'Strategies', path: '/strategies', icon: Sparkles },
  { name: 'Positions', path: '/positions', icon: Activity },
  { name: 'Settings', path: '/settings', icon: Settings },
]

const indices = ['SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'GLD']

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const queryClient = useQueryClient()
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isMarketOpen, setIsMarketOpen] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())
  const [showEmergencyConfirm, setShowEmergencyConfirm] = useState(false)

  // Check if market is open (US market hours: 9:30 AM - 4:00 PM ET, Mon-Fri, excluding holidays)
  useEffect(() => {
    const checkMarketStatus = () => {
      const now = new Date()
      const day = now.getDay() // 0 = Sunday, 6 = Saturday
      const et = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }))
      const hour = et.getHours()
      const minute = et.getMinutes()
      const time = hour * 100 + minute // e.g., 9:30 AM = 930, 4:00 PM = 1600

      // Check for US market holidays (2026)
      const month = et.getMonth() + 1
      const date = et.getDate()
      const year = et.getFullYear()

      const isHoliday = (
        // New Year's Day (Jan 1)
        (month === 1 && date === 1) ||
        // MLK Day (3rd Monday of January)
        (month === 1 && day === 1 && date >= 15 && date <= 21) ||
        // Presidents Day (3rd Monday of February)
        (month === 2 && day === 1 && date >= 15 && date <= 21) ||
        // Good Friday (varies - approximate)
        (month === 4 && date === 3 && year === 2026) ||
        // Memorial Day (last Monday of May)
        (month === 5 && day === 1 && date >= 25) ||
        // Juneteenth (June 19)
        (month === 6 && date === 19) ||
        // Independence Day (July 4, or observed)
        (month === 7 && (date === 4 || (date === 3 && day === 5))) ||
        // Labor Day (1st Monday of September)
        (month === 9 && day === 1 && date <= 7) ||
        // Thanksgiving (4th Thursday of November)
        (month === 11 && day === 4 && date >= 22 && date <= 28) ||
        // Christmas (Dec 25, or observed)
        (month === 12 && (date === 25 || (date === 24 && day === 4) || (date === 26 && day === 1)))
      )

      // Market is open Mon-Fri, 9:30 AM - 4:00 PM ET, excluding holidays
      const isWeekday = day >= 1 && day <= 5
      const isDuringMarketHours = time >= 930 && time < 1600

      setIsMarketOpen(isWeekday && isDuringMarketHours && !isHoliday)
    }

    checkMarketStatus()
    const interval = setInterval(checkMarketStatus, 60000) // Check every minute
    return () => clearInterval(interval)
  }, [])

  // Fetch quotes for all indices - only refetch if market is open
  const { data: quotes } = useQuery({
    queryKey: ['header-quotes', indices],
    queryFn: () => getQuotes(indices),
    refetchInterval: isMarketOpen ? 5000 : false, // Only refetch when market is open
  })

  // Fetch trading mode
  const { data: tradingMode } = useQuery({
    queryKey: ['trading-mode'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/settings/trading-mode')
      if (!response.ok) throw new Error('Failed to fetch trading mode')
      return response.json()
    },
    refetchInterval: 10000, // Check every 10 seconds
  })

  // Emergency stop mutation
  const emergencyStopMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('http://localhost:8000/api/strategies/emergency-stop', {
        method: 'POST',
      })
      if (!response.ok) throw new Error('Failed to execute emergency stop')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
      queryClient.invalidateQueries({ queryKey: ['strategy-positions'] })
      queryClient.invalidateQueries({ queryKey: ['positions'] })
      alert('Emergency stop executed: All strategies stopped and positions closed')
    },
    onError: (error) => {
      alert('Emergency stop failed: ' + error.message)
    },
  })

  // Update current time every second
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  // Rotate through indices every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 4) % indices.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  // Get current four visible indices
  const visibleIndices = [
    quotes?.[currentIndex],
    quotes?.[(currentIndex + 1) % indices.length],
    quotes?.[(currentIndex + 2) % indices.length],
    quotes?.[(currentIndex + 3) % indices.length]
  ]

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      display: 'grid',
      gridTemplateRows: '40px 1fr',
      gridTemplateColumns: '192px 1fr',
      backgroundColor: '#0d1117',
      overflow: 'hidden'
    }}>
      {/* Top Header Bar - Bloomberg Style */}
      <div style={{
        gridColumn: '1 / -1',
        gridRow: '1',
        backgroundColor: '#161b22',
        borderBottom: '1px solid #30363d',
        display: 'flex',
        alignItems: 'center',
        padding: '0 16px',
        gap: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '24px',
            height: '24px',
            background: 'linear-gradient(to bottom right, #FF6B00, #FF8F00)',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <span style={{ color: 'white', fontSize: '12px', fontWeight: 900 }}>A</span>
          </div>
          <span style={{ color: '#FF6B00', fontWeight: 700, fontSize: '14px', letterSpacing: '-0.01em' }}>ALPHAFLOW</span>
          <span style={{ color: '#8b949e', fontSize: '10px', fontFamily: 'monospace' }}>PROFESSIONAL</span>
        </div>

        <div style={{ width: '1px', height: '16px', backgroundColor: '#30363d' }}></div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}>
          <span style={{ color: '#8b949e', fontFamily: 'monospace' }}>MARKET</span>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: isMarketOpen ? '#3fb950' : '#f85149' }}></div>
          <span style={{ color: isMarketOpen ? '#3fb950' : '#f85149', fontFamily: 'monospace', fontWeight: 600 }}>
            {isMarketOpen ? 'OPEN' : 'CLOSED'}
          </span>
        </div>

        <div style={{ width: '1px', height: '16px', backgroundColor: '#30363d' }}></div>

        <div style={{ color: '#8b949e', fontSize: '11px', fontFamily: 'monospace' }}>
          {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }).toUpperCase()}
        </div>

        <div style={{ width: '1px', height: '16px', backgroundColor: '#30363d' }}></div>

        <div style={{ color: '#c9d1d9', fontSize: '11px', fontFamily: 'monospace', fontWeight: 600 }}>
          {currentTime.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
          })}
        </div>

        {/* Trading Mode Indicator */}
        {tradingMode && (
          <>
            <div style={{ width: '1px', height: '16px', backgroundColor: '#30363d' }}></div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 8px',
              borderRadius: '4px',
              backgroundColor: tradingMode.mode === 'live' ? 'rgba(248, 81, 73, 0.15)' : 'rgba(88, 166, 255, 0.15)',
              border: `1px solid ${tradingMode.mode === 'live' ? '#f85149' : '#58a6ff'}`,
            }}>
              <Zap style={{ width: '12px', height: '12px', color: tradingMode.mode === 'live' ? '#f85149' : '#58a6ff' }} />
              <span style={{
                fontSize: '11px',
                fontFamily: 'monospace',
                fontWeight: 700,
                color: tradingMode.mode === 'live' ? '#f85149' : '#58a6ff',
                letterSpacing: '0.05em'
              }}>
                {tradingMode.mode.toUpperCase()} MODE
              </span>
            </div>
          </>
        )}

        {/* Emergency Stop Button */}
        <div style={{ width: '1px', height: '16px', backgroundColor: '#30363d' }}></div>
        <button
          onClick={() => setShowEmergencyConfirm(true)}
          disabled={emergencyStopMutation.isPending}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 12px',
            borderRadius: '4px',
            border: '1px solid #f85149',
            backgroundColor: 'rgba(248, 81, 73, 0.1)',
            color: '#f85149',
            fontSize: '11px',
            fontWeight: 700,
            fontFamily: 'monospace',
            cursor: emergencyStopMutation.isPending ? 'not-allowed' : 'pointer',
            opacity: emergencyStopMutation.isPending ? 0.5 : 1,
            transition: 'all 0.2s',
            letterSpacing: '0.05em'
          }}
          onMouseEnter={(e) => {
            if (!emergencyStopMutation.isPending) {
              e.currentTarget.style.backgroundColor = 'rgba(248, 81, 73, 0.2)'
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(248, 81, 73, 0.1)'
          }}
        >
          <AlertTriangle style={{ width: '14px', height: '14px' }} />
          EMERGENCY STOP
        </button>

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '16px' }}>
          {quotes && quotes.length > 0 && visibleIndices.map((quote) => {
            if (!quote) return null
            const isPositive = quote.change >= 0
            return (
              <div key={quote.symbol} style={{ fontSize: '11px', fontFamily: 'monospace', transition: 'opacity 0.3s', opacity: 1 }}>
                <span style={{ color: '#8b949e' }}>{quote.symbol}</span>
                <span style={{ color: isPositive ? '#3fb950' : '#f85149', marginLeft: '8px', fontWeight: 600 }}>
                  ${quote.price.toFixed(2)}
                </span>
                <span style={{ color: isPositive ? '#3fb950' : '#f85149', marginLeft: '4px', fontSize: '10px' }}>
                  {isPositive ? '+' : ''}{quote.change_percent.toFixed(2)}%
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Sidebar Navigation */}
      <div style={{
        gridColumn: '1',
        gridRow: '2',
        backgroundColor: '#161b22',
        borderRight: '1px solid #30363d',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Navigation */}
        <nav style={{ flex: 1, padding: '8px 0', overflowY: 'auto' }}>
          {navigation.map((item) => {
            const isActive = location.pathname === item.path
            const Icon = item.icon

            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '8px 16px',
                  fontSize: '13px',
                  fontWeight: 500,
                  borderLeft: `2px solid ${isActive ? '#1f6feb' : 'transparent'}`,
                  backgroundColor: isActive ? 'rgba(31, 111, 235, 0.1)' : 'transparent',
                  color: isActive ? '#58a6ff' : '#8b949e',
                  textDecoration: 'none',
                  transition: 'all 0.1s'
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = '#21262d'
                    e.currentTarget.style.color = '#c9d1d9'
                    e.currentTarget.style.borderLeftColor = '#30363d'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'transparent'
                    e.currentTarget.style.color = '#8b949e'
                    e.currentTarget.style.borderLeftColor = 'transparent'
                  }
                }}
              >
                <Icon style={{ width: '16px', height: '16px', marginRight: '12px' }} />
                {item.name}
              </Link>
            )
          })}
        </nav>

      </div>

      {/* Page Content */}
      <main style={{
        gridColumn: '2',
        gridRow: '2',
        backgroundColor: '#0d1117',
        overflow: 'auto',
        position: 'relative'
      }}>
        {children}
      </main>

      {/* Emergency Stop Confirmation Dialog */}
      {showEmergencyConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999
        }}>
          <div style={{
            backgroundColor: '#161b22',
            border: '2px solid #f85149',
            borderRadius: '8px',
            padding: '32px',
            maxWidth: '500px',
            width: '90%'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <AlertTriangle style={{ width: '32px', height: '32px', color: '#f85149' }} />
              <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#f85149', margin: 0 }}>
                EMERGENCY STOP
              </h2>
            </div>

            <p style={{ fontSize: '16px', color: '#c9d1d9', marginBottom: '8px' }}>
              This will immediately:
            </p>

            <ul style={{ color: '#c9d1d9', fontSize: '15px', marginBottom: '24px', paddingLeft: '20px' }}>
              <li style={{ marginBottom: '8px' }}>Stop ALL running strategies</li>
              <li style={{ marginBottom: '8px' }}>Close ALL open positions</li>
              <li style={{ marginBottom: '8px' }}>Cancel ALL pending orders</li>
            </ul>

            <div style={{
              backgroundColor: '#f851491a',
              border: '1px solid #f85149',
              borderRadius: '6px',
              padding: '12px',
              marginBottom: '24px'
            }}>
              <p style={{ fontSize: '13px', color: '#f85149', margin: 0, fontWeight: 600 }}>
                ⚠️ This action cannot be undone. Use only in emergencies.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowEmergencyConfirm(false)}
                disabled={emergencyStopMutation.isPending}
                style={{
                  padding: '12px 24px',
                  borderRadius: '6px',
                  border: '1px solid #30363d',
                  backgroundColor: '#21262d',
                  color: '#c9d1d9',
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: emergencyStopMutation.isPending ? 'not-allowed' : 'pointer',
                  opacity: emergencyStopMutation.isPending ? 0.5 : 1,
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (!emergencyStopMutation.isPending) {
                    e.currentTarget.style.backgroundColor = '#30363d'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#21262d'
                }}
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  emergencyStopMutation.mutate()
                  setShowEmergencyConfirm(false)
                }}
                disabled={emergencyStopMutation.isPending}
                style={{
                  padding: '12px 24px',
                  borderRadius: '6px',
                  border: '1px solid #f85149',
                  backgroundColor: '#f85149',
                  color: '#ffffff',
                  fontSize: '14px',
                  fontWeight: 700,
                  cursor: emergencyStopMutation.isPending ? 'not-allowed' : 'pointer',
                  opacity: emergencyStopMutation.isPending ? 0.5 : 1,
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (!emergencyStopMutation.isPending) {
                    e.currentTarget.style.backgroundColor = '#d63f37'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#f85149'
                }}
              >
                {emergencyStopMutation.isPending ? 'STOPPING...' : 'EXECUTE EMERGENCY STOP'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
