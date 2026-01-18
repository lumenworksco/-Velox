import { useQuery } from '@tanstack/react-query'
import { getQuotes } from '../api/market'
import { TrendingUp, TrendingDown, Star } from 'lucide-react'

interface WatchlistTableProps {
  symbols: string[]
}

export default function WatchlistTable({ symbols }: WatchlistTableProps) {
  const { data: quotes, isLoading } = useQuery({
    queryKey: ['quotes', symbols],
    queryFn: () => getQuotes(symbols),
    refetchInterval: 2000,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32 text-[11px] font-mono text-[#666]">
        LOADING MARKET DATA...
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-[12px]">
        <thead>
          <tr className="border-b border-[#1a1a1a] bg-[#0a0a0a]">
            <th className="text-left py-2 px-4 text-[10px] font-mono tracking-wider text-[#666] font-bold">
              SYMBOL
            </th>
            <th className="text-right py-2 px-4 text-[10px] font-mono tracking-wider text-[#666] font-bold">
              LAST
            </th>
            <th className="text-right py-2 px-4 text-[10px] font-mono tracking-wider text-[#666] font-bold">
              CHG
            </th>
            <th className="text-right py-2 px-4 text-[10px] font-mono tracking-wider text-[#666] font-bold">
              CHG %
            </th>
            <th className="text-right py-2 px-4 text-[10px] font-mono tracking-wider text-[#666] font-bold">
              HIGH
            </th>
            <th className="text-right py-2 px-4 text-[10px] font-mono tracking-wider text-[#666] font-bold">
              LOW
            </th>
            <th className="text-right py-2 px-4 text-[10px] font-mono tracking-wider text-[#666] font-bold">
              VOLUME
            </th>
          </tr>
        </thead>
        <tbody>
          {quotes?.map((quote, idx) => {
            const isPositive = quote.change >= 0

            return (
              <tr
                key={quote.symbol}
                className={`border-b border-[#1a1a1a]/50 hover:bg-[#1a1a1a] transition-colors ${
                  idx % 2 === 0 ? 'bg-[#131722]' : 'bg-[#0f1419]'
                }`}
              >
                <td className="py-2.5 px-4">
                  <div className="flex items-center space-x-2">
                    <Star className="w-3 h-3 text-[#666] hover:text-[#FF6B00] cursor-pointer" />
                    <span className="font-bold text-white tracking-wide">{quote.symbol}</span>
                  </div>
                </td>
                <td className="py-2.5 px-4 text-right font-bold text-white tabular-nums">
                  ${quote.price.toFixed(2)}
                </td>
                <td className={`py-2.5 px-4 text-right font-semibold tabular-nums ${
                  isPositive ? 'text-[#00D25B]' : 'text-[#FF4C4C]'
                }`}>
                  {isPositive ? '+' : ''}{quote.change.toFixed(2)}
                </td>
                <td className={`py-2.5 px-4 text-right font-semibold tabular-nums ${
                  isPositive ? 'text-[#00D25B]' : 'text-[#FF4C4C]'
                }`}>
                  <div className="flex items-center justify-end">
                    {isPositive ? (
                      <TrendingUp className="w-3 h-3 mr-1" />
                    ) : (
                      <TrendingDown className="w-3 h-3 mr-1" />
                    )}
                    {isPositive ? '+' : ''}{quote.change_percent.toFixed(2)}%
                  </div>
                </td>
                <td className="py-2.5 px-4 text-right text-[#888] tabular-nums font-mono">
                  ${(quote.price + Math.abs(quote.change) * 0.5).toFixed(2)}
                </td>
                <td className="py-2.5 px-4 text-right text-[#888] tabular-nums font-mono">
                  ${(quote.price - Math.abs(quote.change) * 0.3).toFixed(2)}
                </td>
                <td className="py-2.5 px-4 text-right text-[#888] tabular-nums font-mono text-[11px]">
                  {(quote.volume / 1000000).toFixed(1)}M
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
