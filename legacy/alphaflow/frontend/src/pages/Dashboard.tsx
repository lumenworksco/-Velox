import { useQuery } from '@tanstack/react-query'
import EquityChart from '../components/EquityChart'
import WatchlistTable from '../components/WatchlistTable'
import { getPortfolioSummary, getEquityHistory } from '../api/portfolio'
import { TrendingUp, TrendingDown } from 'lucide-react'

export default function Dashboard() {
  const { data: portfolio } = useQuery({
    queryKey: ['portfolio'],
    queryFn: getPortfolioSummary,
    refetchInterval: 5000,
  })

  const { data: equityHistory } = useQuery({
    queryKey: ['equity-history'],
    queryFn: () => getEquityHistory(30),
  })

  const dayPnlPositive = (portfolio?.day_pnl || 0) >= 0
  const totalPnlPositive = (portfolio?.total_pnl || 0) >= 0

  return (
    <div className="h-full flex flex-col bg-[#0A0E27]">
      {/* Top Metrics Bar - Bloomberg Style */}
      <div className="bg-[#000000] border-b border-[#1a1a1a] px-4 py-2">
        <div className="grid grid-cols-4 gap-6">
          {/* Portfolio Value */}
          <div className="flex items-baseline space-x-3">
            <div>
              <div className="text-[10px] font-mono text-[#666] tracking-wider mb-0.5">PORTFOLIO VALUE</div>
              <div className="text-[22px] font-bold text-white tabular-nums tracking-tight">
                ${(portfolio?.total_value || 105000).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
            <div className={`flex items-center text-[13px] font-semibold ${totalPnlPositive ? 'text-[#00D25B]' : 'text-[#FF4C4C]'}`}>
              {totalPnlPositive ? <TrendingUp className="w-3.5 h-3.5 mr-1" /> : <TrendingDown className="w-3.5 h-3.5 mr-1" />}
              {totalPnlPositive ? '+' : ''}{((portfolio?.total_pnl_percent || 5.0)).toFixed(2)}%
            </div>
          </div>

          {/* Day P&L */}
          <div className="flex items-baseline space-x-3">
            <div>
              <div className="text-[10px] font-mono text-[#666] tracking-wider mb-0.5">DAY P&L</div>
              <div className={`text-[22px] font-bold tabular-nums tracking-tight ${dayPnlPositive ? 'text-[#00D25B]' : 'text-[#FF4C4C]'}`}>
                {dayPnlPositive ? '+' : ''}${Math.abs(portfolio?.day_pnl || 1250).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
            <div className={`flex items-center text-[13px] font-semibold ${dayPnlPositive ? 'text-[#00D25B]' : 'text-[#FF4C4C]'}`}>
              {dayPnlPositive ? <TrendingUp className="w-3.5 h-3.5 mr-1" /> : <TrendingDown className="w-3.5 h-3.5 mr-1" />}
              {dayPnlPositive ? '+' : ''}{((portfolio?.day_pnl_percent || 1.2)).toFixed(2)}%
            </div>
          </div>

          {/* Total P&L */}
          <div className="flex items-baseline space-x-3">
            <div>
              <div className="text-[10px] font-mono text-[#666] tracking-wider mb-0.5">TOTAL P&L</div>
              <div className={`text-[22px] font-bold tabular-nums tracking-tight ${totalPnlPositive ? 'text-[#00D25B]' : 'text-[#FF4C4C]'}`}>
                {totalPnlPositive ? '+' : ''}${Math.abs(portfolio?.total_pnl || 5000).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
          </div>

          {/* Buying Power */}
          <div>
            <div className="text-[10px] font-mono text-[#666] tracking-wider mb-0.5">BUYING POWER</div>
            <div className="text-[22px] font-bold text-white tabular-nums tracking-tight">
              ${(portfolio?.buying_power || 200000).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="flex-1 grid grid-cols-3 gap-px bg-[#1a1a1a] overflow-auto">
        {/* Left Panel - Equity Curve */}
        <div className="col-span-2 bg-[#131722] flex flex-col">
          <div className="border-b border-[#1a1a1a] px-4 py-2 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <h2 className="text-[12px] font-bold text-white tracking-wide">EQUITY CURVE</h2>
              <span className="text-[10px] font-mono text-[#666]">30D</span>
            </div>
            <div className="flex items-center space-x-4 text-[11px] font-mono">
              <div>
                <span className="text-[#666]">HIGH</span>
                <span className="text-[#00D25B] ml-2 font-semibold">$107,245</span>
              </div>
              <div>
                <span className="text-[#666]">LOW</span>
                <span className="text-[#FF4C4C] ml-2 font-semibold">$98,120</span>
              </div>
              <div>
                <span className="text-[#666]">AVG</span>
                <span className="text-white ml-2 font-semibold">$102,480</span>
              </div>
            </div>
          </div>
          <div className="flex-1 p-4">
            <EquityChart data={equityHistory || []} />
          </div>
        </div>

        {/* Right Panel - Quick Stats */}
        <div className="bg-[#131722] flex flex-col">
          <div className="border-b border-[#1a1a1a] px-4 py-2">
            <h2 className="text-[12px] font-bold text-white tracking-wide">PERFORMANCE</h2>
          </div>
          <div className="flex-1 overflow-auto">
            <div className="p-4 space-y-3">
              {/* Metric Row */}
              <div className="flex justify-between items-center pb-2 border-b border-[#1a1a1a]">
                <span className="text-[11px] font-mono text-[#888]">SHARPE RATIO</span>
                <span className="text-[13px] font-bold text-white tabular-nums">1.84</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-[#1a1a1a]">
                <span className="text-[11px] font-mono text-[#888]">MAX DRAWDOWN</span>
                <span className="text-[13px] font-bold text-[#FF4C4C] tabular-nums">-8.42%</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-[#1a1a1a]">
                <span className="text-[11px] font-mono text-[#888]">WIN RATE</span>
                <span className="text-[13px] font-bold text-[#00D25B] tabular-nums">67.3%</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-[#1a1a1a]">
                <span className="text-[11px] font-mono text-[#888]">PROFIT FACTOR</span>
                <span className="text-[13px] font-bold text-white tabular-nums">2.14</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-[#1a1a1a]">
                <span className="text-[11px] font-mono text-[#888]">TOTAL TRADES</span>
                <span className="text-[13px] font-bold text-white tabular-nums">142</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-[#1a1a1a]">
                <span className="text-[11px] font-mono text-[#888]">AVG TRADE</span>
                <span className="text-[13px] font-bold text-[#00D25B] tabular-nums">+$35.21</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-[#1a1a1a]">
                <span className="text-[11px] font-mono text-[#888]">BEST TRADE</span>
                <span className="text-[13px] font-bold text-[#00D25B] tabular-nums">+$428.50</span>
              </div>
              <div className="flex justify-between items-center pb-2">
                <span className="text-[11px] font-mono text-[#888]">WORST TRADE</span>
                <span className="text-[13px] font-bold text-[#FF4C4C] tabular-nums">-$192.30</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Panel - Watchlist */}
        <div className="col-span-3 bg-[#131722] flex flex-col max-h-[400px]">
          <div className="border-b border-[#1a1a1a] px-4 py-2">
            <h2 className="text-[12px] font-bold text-white tracking-wide">WATCHLIST</h2>
          </div>
          <div className="flex-1 overflow-auto">
            <WatchlistTable symbols={['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'NFLX']} />
          </div>
        </div>
      </div>
    </div>
  )
}
