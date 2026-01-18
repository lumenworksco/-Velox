import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  TrendingUp,
  BarChart3,
  TestTube2,
  Sparkles,
  Settings
} from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Trading', path: '/trading', icon: TrendingUp },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  { name: 'Backtest', path: '/backtest', icon: TestTube2 },
  { name: 'Strategies', path: '/strategies', icon: Sparkles },
  { name: 'Settings', path: '/settings', icon: Settings },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div className="flex h-screen bg-primary-bg">
      {/* Sidebar */}
      <div className="w-64 bg-primary-surface border-r border-primary-border flex flex-col">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-primary-border">
          <h1 className="text-xl font-bold text-accent-blue">AlphaFlow</h1>
          <span className="ml-2 text-xs text-text-tertiary">v7.0</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.path
            const Icon = item.icon

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex items-center px-3 py-2.5 rounded-lg text-sm font-medium
                  transition-colors duration-150
                  ${isActive
                    ? 'bg-accent-blue text-white'
                    : 'text-text-secondary hover:bg-primary-elevated hover:text-text-primary'
                  }
                `}
              >
                <Icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-primary-border">
          <div className="flex items-center justify-between text-xs text-text-tertiary">
            <span>Market</span>
            <span className="text-semantic-positive">● Open</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-primary-surface border-b border-primary-border flex items-center justify-between px-6">
          <div className="flex items-center space-x-4">
            <div className="text-text-secondary text-sm">
              {new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="px-3 py-1.5 rounded-lg bg-accent-blue/10 text-accent-blue text-sm font-medium">
              PAPER TRADING
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
