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
    <div style={{ backgroundColor: '#0d1117', borderRadius: '6px', border: '1px solid #30363d', padding: '24px' }}>
      <div style={{ borderBottom: '1px solid #30363d', paddingBottom: '12px', marginBottom: '16px' }}>
        <h3 style={{ fontSize: '12px', fontWeight: 700, color: '#c9d1d9', letterSpacing: '0.03em', margin: 0 }}>PLACE ORDER</h3>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Side Selection */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          <button
            type="button"
            onClick={() => setSide('buy')}
            style={{
              padding: '12px',
              borderRadius: '6px',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              backgroundColor: side === 'buy' ? '#3fb950' : '#161b22',
              color: side === 'buy' ? '#ffffff' : '#8b949e',
              transition: 'all 0.1s'
            }}
            onMouseEnter={(e) => {
              if (side !== 'buy') e.currentTarget.style.backgroundColor = '#21262d'
            }}
            onMouseLeave={(e) => {
              if (side !== 'buy') e.currentTarget.style.backgroundColor = '#161b22'
            }}
          >
            <TrendingUp style={{ width: '18px', height: '18px' }} />
            <span>BUY</span>
          </button>
          <button
            type="button"
            onClick={() => setSide('sell')}
            style={{
              padding: '12px',
              borderRadius: '6px',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              backgroundColor: side === 'sell' ? '#f85149' : '#161b22',
              color: side === 'sell' ? '#ffffff' : '#8b949e',
              transition: 'all 0.1s'
            }}
            onMouseEnter={(e) => {
              if (side !== 'sell') e.currentTarget.style.backgroundColor = '#21262d'
            }}
            onMouseLeave={(e) => {
              if (side !== 'sell') e.currentTarget.style.backgroundColor = '#161b22'
            }}
          >
            <TrendingDown style={{ width: '18px', height: '18px' }} />
            <span>SELL</span>
          </button>
        </div>

        {/* Order Type */}
        <div>
          <label style={{ display: 'block', fontSize: '11px', fontFamily: 'monospace', color: '#8b949e', marginBottom: '8px', letterSpacing: '0.05em' }}>
            ORDER TYPE
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <button
              type="button"
              onClick={() => setOrderType('market')}
              style={{
                padding: '8px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 500,
                border: 'none',
                cursor: 'pointer',
                backgroundColor: orderType === 'market' ? '#58a6ff' : '#161b22',
                color: orderType === 'market' ? '#ffffff' : '#8b949e',
                transition: 'all 0.1s'
              }}
              onMouseEnter={(e) => {
                if (orderType !== 'market') e.currentTarget.style.backgroundColor = '#21262d'
              }}
              onMouseLeave={(e) => {
                if (orderType !== 'market') e.currentTarget.style.backgroundColor = '#161b22'
              }}
            >
              Market
            </button>
            <button
              type="button"
              onClick={() => setOrderType('limit')}
              style={{
                padding: '8px',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 500,
                border: 'none',
                cursor: 'pointer',
                backgroundColor: orderType === 'limit' ? '#58a6ff' : '#161b22',
                color: orderType === 'limit' ? '#ffffff' : '#8b949e',
                transition: 'all 0.1s'
              }}
              onMouseEnter={(e) => {
                if (orderType !== 'limit') e.currentTarget.style.backgroundColor = '#21262d'
              }}
              onMouseLeave={(e) => {
                if (orderType !== 'limit') e.currentTarget.style.backgroundColor = '#161b22'
              }}
            >
              Limit
            </button>
          </div>
        </div>

        {/* Quantity */}
        <div>
          <label style={{ display: 'block', fontSize: '11px', fontFamily: 'monospace', color: '#8b949e', marginBottom: '8px', letterSpacing: '0.05em' }}>
            QUANTITY
          </label>
          <div style={{ position: 'relative' }}>
            <Hash style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', width: '18px', height: '18px', color: '#8b949e' }} />
            <input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              style={{
                width: '100%',
                backgroundColor: '#161b22',
                border: '1px solid #30363d',
                borderRadius: '6px',
                padding: '10px 16px 10px 38px',
                color: '#c9d1d9',
                fontSize: '14px',
                outline: 'none',
                fontFamily: 'monospace'
              }}
              placeholder="10"
              min="1"
              required
            />
          </div>
        </div>

        {/* Limit Price */}
        {orderType === 'limit' && (
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontFamily: 'monospace', color: '#8b949e', marginBottom: '8px', letterSpacing: '0.05em' }}>
              LIMIT PRICE
            </label>
            <div style={{ position: 'relative' }}>
              <DollarSign style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', width: '18px', height: '18px', color: '#8b949e' }} />
              <input
                type="number"
                value={limitPrice}
                onChange={(e) => setLimitPrice(e.target.value)}
                style={{
                  width: '100%',
                  backgroundColor: '#161b22',
                  border: '1px solid #30363d',
                  borderRadius: '6px',
                  padding: '10px 16px 10px 38px',
                  color: '#c9d1d9',
                  fontSize: '14px',
                  outline: 'none',
                  fontFamily: 'monospace'
                }}
                placeholder={currentPrice?.toFixed(2)}
                step="0.01"
                required
              />
            </div>
          </div>
        )}

        {/* Order Summary */}
        <div style={{ backgroundColor: '#161b22', borderRadius: '6px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
            <span style={{ color: '#8b949e' }}>Current Price</span>
            <span style={{ color: '#c9d1d9', fontFamily: 'monospace' }}>${currentPrice?.toFixed(2) || '—'}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
            <span style={{ color: '#8b949e' }}>Quantity</span>
            <span style={{ color: '#c9d1d9', fontFamily: 'monospace' }}>{quantity}</span>
          </div>
          <div style={{ height: '1px', backgroundColor: '#30363d', margin: '8px 0' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#c9d1d9', fontWeight: 500 }}>Estimated {side === 'buy' ? 'Cost' : 'Proceeds'}</span>
            <span style={{ color: '#c9d1d9', fontWeight: 700, fontFamily: 'monospace' }}>${estimatedCost}</span>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={placeOrderMutation.isPending}
          style={{
            width: '100%',
            padding: '14px',
            borderRadius: '6px',
            fontWeight: 700,
            fontSize: '14px',
            border: 'none',
            cursor: placeOrderMutation.isPending ? 'not-allowed' : 'pointer',
            backgroundColor: side === 'buy' ? '#3fb950' : '#f85149',
            color: '#ffffff',
            opacity: placeOrderMutation.isPending ? 0.5 : 1,
            transition: 'all 0.1s',
            letterSpacing: '0.03em'
          }}
        >
          {placeOrderMutation.isPending ? 'PLACING ORDER...' : `${side.toUpperCase()} ${symbol}`}
        </button>

        {/* Error Message */}
        {placeOrderMutation.isError && (
          <div style={{ backgroundColor: 'rgba(248, 81, 73, 0.1)', border: '1px solid rgba(248, 81, 73, 0.3)', borderRadius: '6px', padding: '12px', color: '#f85149', fontSize: '13px' }}>
            Failed to place order. Please try again.
          </div>
        )}

        {/* Success Message */}
        {placeOrderMutation.isSuccess && (
          <div style={{ backgroundColor: 'rgba(63, 185, 80, 0.1)', border: '1px solid rgba(63, 185, 80, 0.3)', borderRadius: '6px', padding: '12px', color: '#3fb950', fontSize: '13px' }}>
            Order placed successfully!
          </div>
        )}
      </form>
    </div>
  )
}
