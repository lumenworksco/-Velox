import { useQuery } from '@tanstack/react-query'
import MetricCard from '../components/MetricCard'
import WatchlistTable from '../components/WatchlistTable'
import EquityChart from '../components/EquityChart'
import { getPortfolioSummary, getEquityHistory } from '../api/portfolio'

export default function Dashboard() {
  const { data: portfolio } = useQuery({
    queryKey: ['portfolio'],
    queryFn: getPortfolioSummary,
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  const { data: equityHistory } = useQuery({
    queryKey: ['equity-history'],
    queryFn: () => getEquityHistory(30),
  })

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-text-primary">Portfolio Overview</h1>
        <button className="px-4 py-2 bg-accent-blue hover:bg-accent-blue-hover rounded-lg text-white text-sm font-medium transition-colors">
          Refresh Data
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Portfolio Value"
          value={`$${portfolio?.total_value.toLocaleString() || '0'}`}
          change={portfolio?.total_pnl_percent || 0}
        />
        <MetricCard
          label="Day P&L"
          value={`$${portfolio?.day_pnl.toLocaleString() || '0'}`}
          change={portfolio?.day_pnl_percent || 0}
        />
        <MetricCard
          label="Total P&L"
          value={`$${portfolio?.total_pnl.toLocaleString() || '0'}`}
          change={portfolio?.total_pnl_percent || 0}
        />
        <MetricCard
          label="Buying Power"
          value={`$${portfolio?.buying_power.toLocaleString() || '0'}`}
        />
      </div>

      {/* Equity Curve */}
      <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
        <h2 className="text-lg font-semibold text-text-primary mb-4">Equity Curve</h2>
        <EquityChart data={equityHistory || []} />
      </div>

      {/* Watchlist */}
      <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
        <h2 className="text-lg font-semibold text-text-primary mb-4">Watchlist</h2>
        <WatchlistTable symbols={['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']} />
      </div>
    </div>
  )
}
