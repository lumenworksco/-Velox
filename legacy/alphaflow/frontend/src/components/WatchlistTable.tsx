import { useQuery } from '@tanstack/react-query'
import { getQuotes } from '../api/market'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface WatchlistTableProps {
  symbols: string[]
}

export default function WatchlistTable({ symbols }: WatchlistTableProps) {
  const { data: quotes, isLoading } = useQuery({
    queryKey: ['quotes', symbols],
    queryFn: () => getQuotes(symbols),
    refetchInterval: 2000, // Refresh every 2 seconds
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="pulse text-text-secondary">Loading market data...</div>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-primary-border">
            <th className="text-left py-3 px-4 text-xs uppercase tracking-wider text-text-secondary font-bold">
              Symbol
            </th>
            <th className="text-right py-3 px-4 text-xs uppercase tracking-wider text-text-secondary font-bold">
              Price
            </th>
            <th className="text-right py-3 px-4 text-xs uppercase tracking-wider text-text-secondary font-bold">
              Change
            </th>
            <th className="text-right py-3 px-4 text-xs uppercase tracking-wider text-text-secondary font-bold">
              Change %
            </th>
            <th className="text-right py-3 px-4 text-xs uppercase tracking-wider text-text-secondary font-bold">
              Volume
            </th>
          </tr>
        </thead>
        <tbody>
          {quotes?.map((quote) => {
            const isPositive = quote.change >= 0

            return (
              <tr
                key={quote.symbol}
                className="border-b border-primary-border/50 hover:bg-primary-elevated transition-colors"
              >
                <td className="py-4 px-4">
                  <span className="font-semibold text-text-primary">{quote.symbol}</span>
                </td>
                <td className="py-4 px-4 text-right tabular-nums text-text-primary font-medium">
                  ${quote.price.toFixed(2)}
                </td>
                <td className={`py-4 px-4 text-right tabular-nums font-medium ${
                  isPositive ? 'text-semantic-positive' : 'text-semantic-negative'
                }`}>
                  {isPositive ? '+' : ''}{quote.change.toFixed(2)}
                </td>
                <td className={`py-4 px-4 text-right ${
                  isPositive ? 'text-semantic-positive' : 'text-semantic-negative'
                }`}>
                  <div className="flex items-center justify-end font-medium tabular-nums">
                    {isPositive ? (
                      <TrendingUp className="w-4 h-4 mr-1" />
                    ) : (
                      <TrendingDown className="w-4 h-4 mr-1" />
                    )}
                    {isPositive ? '+' : ''}{quote.change_percent.toFixed(2)}%
                  </div>
                </td>
                <td className="py-4 px-4 text-right tabular-nums text-text-secondary text-sm">
                  {(quote.volume / 1000000).toFixed(2)}M
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
