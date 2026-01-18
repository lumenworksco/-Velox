import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { placeOrder } from '../api/trading'
import { TrendingUp, TrendingDown, DollarSign, Hash } from 'lucide-react'

interface OrderEntryProps {
  symbol: string
  currentPrice?: number
}

export default function OrderEntry({ symbol, currentPrice }: OrderEntryProps) {
  const [side, setSide] = useState<'buy' | 'sell'>('buy')
  const [orderType, setOrderType] = useState<'market' | 'limit'>('market')
  const [quantity, setQuantity] = useState<string>('10')
  const [limitPrice, setLimitPrice] = useState<string>(currentPrice?.toFixed(2) || '')

  const queryClient = useQueryClient()

  const placeOrderMutation = useMutation({
    mutationFn: placeOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      queryClient.invalidateQueries({ queryKey: ['positions'] })
      // Reset form
      setQuantity('10')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    placeOrderMutation.mutate({
      symbol,
      side,
      quantity: parseInt(quantity),
      order_type: orderType,
      limit_price: orderType === 'limit' ? parseFloat(limitPrice) : undefined,
    })
  }

  const estimatedCost = currentPrice && quantity
    ? (parseFloat(quantity) * (orderType === 'limit' ? parseFloat(limitPrice || '0') : currentPrice)).toFixed(2)
    : '0.00'

  return (
    <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
      <h3 className="text-lg font-semibold text-text-primary mb-4">Place Order</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Side Selection */}
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => setSide('buy')}
            className={`py-3 rounded-lg font-semibold transition-all flex items-center justify-center space-x-2 ${
              side === 'buy'
                ? 'bg-semantic-positive text-white'
                : 'bg-primary-elevated text-text-secondary hover:bg-primary-hover'
            }`}
          >
            <TrendingUp className="w-5 h-5" />
            <span>BUY</span>
          </button>
          <button
            type="button"
            onClick={() => setSide('sell')}
            className={`py-3 rounded-lg font-semibold transition-all flex items-center justify-center space-x-2 ${
              side === 'sell'
                ? 'bg-semantic-negative text-white'
                : 'bg-primary-elevated text-text-secondary hover:bg-primary-hover'
            }`}
          >
            <TrendingDown className="w-5 h-5" />
            <span>SELL</span>
          </button>
        </div>

        {/* Order Type */}
        <div>
          <label className="block text-sm font-medium text-text-secondary mb-2">
            Order Type
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setOrderType('market')}
              className={`py-2 rounded-lg text-sm font-medium transition-colors ${
                orderType === 'market'
                  ? 'bg-accent-blue text-white'
                  : 'bg-primary-elevated text-text-secondary hover:bg-primary-hover'
              }`}
            >
              Market
            </button>
            <button
              type="button"
              onClick={() => setOrderType('limit')}
              className={`py-2 rounded-lg text-sm font-medium transition-colors ${
                orderType === 'limit'
                  ? 'bg-accent-blue text-white'
                  : 'bg-primary-elevated text-text-secondary hover:bg-primary-hover'
              }`}
            >
              Limit
            </button>
          </div>
        </div>

        {/* Quantity */}
        <div>
          <label className="block text-sm font-medium text-text-secondary mb-2">
            Quantity
          </label>
          <div className="relative">
            <Hash className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-tertiary" />
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="w-full bg-primary-elevated border border-primary-border rounded-lg py-3 pl-10 pr-4 text-text-primary focus:outline-none focus:border-accent-blue"
              placeholder="10"
              min="1"
              required
            />
          </div>
        </div>

        {/* Limit Price (if limit order) */}
        {orderType === 'limit' && (
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Limit Price
            </label>
            <div className="relative">
              <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-tertiary" />
              <input
                type="number"
                value={limitPrice}
                onChange={(e) => setLimitPrice(e.target.value)}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-3 pl-10 pr-4 text-text-primary focus:outline-none focus:border-accent-blue"
                placeholder={currentPrice?.toFixed(2)}
                step="0.01"
                required
              />
            </div>
          </div>
        )}

        {/* Order Summary */}
        <div className="bg-primary-elevated rounded-lg p-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-text-secondary">Current Price</span>
            <span className="text-text-primary font-mono">${currentPrice?.toFixed(2) || '—'}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-text-secondary">Quantity</span>
            <span className="text-text-primary font-mono">{quantity}</span>
          </div>
          <div className="h-px bg-primary-border my-2" />
          <div className="flex justify-between">
            <span className="text-text-primary font-medium">Estimated {side === 'buy' ? 'Cost' : 'Proceeds'}</span>
            <span className="text-text-primary font-bold font-mono">${estimatedCost}</span>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={placeOrderMutation.isPending}
          className={`w-full py-4 rounded-lg font-bold text-white transition-all ${
            side === 'buy'
              ? 'bg-semantic-positive hover:bg-semantic-positive/90'
              : 'bg-semantic-negative hover:bg-semantic-negative/90'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {placeOrderMutation.isPending ? 'Placing Order...' : `${side.toUpperCase()} ${symbol}`}
        </button>

        {/* Error Message */}
        {placeOrderMutation.isError && (
          <div className="bg-semantic-negative/10 border border-semantic-negative/30 rounded-lg p-3 text-semantic-negative text-sm">
            Failed to place order. Please try again.
          </div>
        )}

        {/* Success Message */}
        {placeOrderMutation.isSuccess && (
          <div className="bg-semantic-positive/10 border border-semantic-positive/30 rounded-lg p-3 text-semantic-positive text-sm">
            Order placed successfully!
          </div>
        )}
      </form>
    </div>
  )
}
