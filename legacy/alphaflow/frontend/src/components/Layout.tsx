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
    <div className="flex h-screen bg-primary-bg overflow-hidden">
      {/* Top Header Bar - Bloomberg Style */}
      <div className="fixed top-0 left-0 right-0 h-10 bg-[#000000] border-b border-[#1a1a1a] flex items-center px-4 z-50">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-gradient-to-br from-[#FF6B00] to-[#FF8F00] rounded flex items-center justify-center">
              <span className="text-white text-xs font-black">A</span>
            </div>
            <span className="text-[#FF6B00] font-bold text-sm tracking-tight">ALPHAFLOW</span>
            <span className="text-[#666] text-[10px] font-mono">PROFESSIONAL</span>
          </div>

          <div className="h-4 w-px bg-[#333]"></div>

          <div className="flex items-center space-x-1 text-[11px]">
            <span className="text-[#666] font-mono">MARKET</span>
            <div className="w-1.5 h-1.5 rounded-full bg-[#00D25B] animate-pulse"></div>
            <span className="text-[#00D25B] font-mono font-semibold">OPEN</span>
          </div>

          <div className="h-4 w-px bg-[#333]"></div>

          <div className="text-[11px] font-mono text-[#666]">
            {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }).toUpperCase()}
          </div>

          <div className="h-4 w-px bg-[#333]"></div>

          <div className="px-2 py-0.5 bg-[#2962FF]/20 border border-[#2962FF]/40 rounded">
            <span className="text-[#2962FF] text-[10px] font-bold tracking-wide">PAPER MODE</span>
          </div>
        </div>

        <div className="ml-auto flex items-center space-x-4">
          <div className="text-[11px] font-mono">
            <span className="text-[#666]">SPY</span>
            <span className="text-[#00D25B] ml-2 font-semibold">478.32</span>
            <span className="text-[#00D25B] ml-1 text-[10px]">+0.42%</span>
          </div>
          <div className="text-[11px] font-mono">
            <span className="text-[#666]">QQQ</span>
            <span className="text-[#00D25B] ml-2 font-semibold">412.18</span>
            <span className="text-[#00D25B] ml-1 text-[10px]">+0.58%</span>
          </div>
        </div>
      </div>

      {/* Main Layout */}
      <div className="flex w-full mt-10">
        {/* Sidebar Navigation */}
        <div className="w-48 bg-[#0a0a0a] border-r border-[#1a1a1a] flex flex-col">
          {/* Navigation */}
          <nav className="flex-1 py-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.path
              const Icon = item.icon

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center px-4 py-2 text-[13px] font-medium
                    transition-all duration-100 border-l-2
                    ${isActive
                      ? 'bg-[#2962FF]/10 border-[#2962FF] text-[#2962FF]'
                      : 'border-transparent text-[#888] hover:bg-[#1a1a1a] hover:text-[#E0E3EB] hover:border-[#333]'
                    }
                  `}
                >
                  <Icon className="w-4 h-4 mr-3" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* System Info */}
          <div className="p-3 border-t border-[#1a1a1a] space-y-1">
            <div className="flex justify-between text-[10px] font-mono">
              <span className="text-[#666]">CPU</span>
              <span className="text-[#00D25B]">12%</span>
            </div>
            <div className="flex justify-between text-[10px] font-mono">
              <span className="text-[#666]">MEM</span>
              <span className="text-[#00D25B]">2.4GB</span>
            </div>
            <div className="flex justify-between text-[10px] font-mono">
              <span className="text-[#666]">LAT</span>
              <span className="text-[#00D25B]">8ms</span>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <main className="flex-1 overflow-auto bg-primary-bg">
          {children}
        </main>
      </div>
    </div>
  )
}
