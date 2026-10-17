import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Key, Shield, Info } from 'lucide-react'
import { getSettings, updateAPIKeys, updateRiskSettings } from '../api/settings'

export default function Settings() {
  const queryClient = useQueryClient()

  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: getSettings,
  })

  const [alpacaApiKey, setAlpacaApiKey] = useState('')
  const [alpacaSecretKey, setAlpacaSecretKey] = useState('')
  const [paperTrading, setPaperTrading] = useState(true)
  const [maxPositionSize, setMaxPositionSize] = useState('10000')
  const [maxDailyLoss, setMaxDailyLoss] = useState('5000')
  const [stopLoss, setStopLoss] = useState('2')
  const [takeProfit, setTakeProfit] = useState('5')

  useEffect(() => {
    if (settings) {
      setPaperTrading(settings.paper_trading)
      setMaxPositionSize(settings.max_position_size.toString())
      setMaxDailyLoss(settings.max_daily_loss.toString())
      setStopLoss(settings.stop_loss_percent.toString())
      setTakeProfit(settings.take_profit_percent.toString())
    }
  }, [settings])

  const updateKeysMutation = useMutation({
    mutationFn: updateAPIKeys,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      setAlpacaApiKey('')
      setAlpacaSecretKey('')
    },
  })

  const updateRiskMutation = useMutation({
    mutationFn: updateRiskSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
    },
  })

  const handleSaveKeys = () => {
    updateKeysMutation.mutate({
      alpaca_api_key: alpacaApiKey || undefined,
      alpaca_secret_key: alpacaSecretKey || undefined,
      paper_trading: paperTrading,
    })
  }

  const handleSaveRisk = () => {
    updateRiskMutation.mutate({
      max_position_size: parseFloat(maxPositionSize),
      max_daily_loss: parseFloat(maxDailyLoss),
      stop_loss_percent: parseFloat(stopLoss),
      take_profit_percent: parseFloat(takeProfit),
    })
  }

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#0d1117', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ backgroundColor: '#161b22', borderBottom: '1px solid #30363d', padding: '16px 24px' }}>
        <div>
          <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#c9d1d9', margin: '0 0 4px 0' }}>Settings</h1>
          <p style={{ fontSize: '13px', color: '#8b949e', margin: 0 }}>Configure your trading platform preferences</p>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
        <div style={{ maxWidth: '900px', display: 'flex', flexDirection: 'column', gap: '24px' }}>

          {/* Info Banner */}
          <div style={{ backgroundColor: 'rgba(88, 166, 255, 0.1)', border: '1px solid rgba(88, 166, 255, 0.3)', borderRadius: '8px', padding: '16px', display: 'flex', gap: '12px' }}>
            <Info style={{ width: '20px', height: '20px', color: '#58a6ff', flexShrink: 0, marginTop: '2px' }} />
            <div style={{ fontSize: '13px', color: '#c9d1d9', lineHeight: '1.5' }}>
              <div style={{ fontWeight: 600, marginBottom: '4px' }}>Paper Trading Mode Active</div>
              <div style={{ color: '#8b949e' }}>
                You are currently trading with simulated funds. Enable paper trading toggle to use Alpaca's paper trading account,
                or disable it to trade with real money (requires live API keys).
              </div>
            </div>
          </div>

          {/* API Keys */}
          <div style={{ backgroundColor: '#161b22', border: '1px solid #30363d', borderRadius: '8px', padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Key style={{ width: '20px', height: '20px', color: '#58a6ff' }} />
                <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#c9d1d9', margin: 0 }}>Alpaca API Keys</h2>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <label style={{ fontSize: '13px', color: '#8b949e', fontWeight: 500 }}>Paper Trading</label>
                <label style={{ position: 'relative', display: 'inline-block', width: '52px', height: '28px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={paperTrading}
                    onChange={(e) => setPaperTrading(e.target.checked)}
                    style={{ opacity: 0, width: 0, height: 0 }}
                  />
                  <span style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: paperTrading ? '#3fb950' : '#30363d',
                    borderRadius: '28px',
                    transition: 'background-color 0.2s'
                  }}>
                    <span style={{
                      position: 'absolute',
                      content: '',
                      height: '20px',
                      width: '20px',
                      left: paperTrading ? '28px' : '4px',
                      bottom: '4px',
                      backgroundColor: '#ffffff',
                      borderRadius: '50%',
                      transition: 'left 0.2s'
                    }}></span>
                  </span>
                </label>
              </div>
            </div>

            <div style={{ fontSize: '13px', color: '#8b949e', marginBottom: '16px', lineHeight: '1.5' }}>
              Get your API keys from <a href="https://alpaca.markets" target="_blank" rel="noopener noreferrer" style={{ color: '#58a6ff', textDecoration: 'none' }}>alpaca.markets</a>.
              Make sure to use paper trading keys for testing.
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#8b949e', marginBottom: '8px' }}>
                  Alpaca API Key {settings?.alpaca_api_key && <span style={{ color: '#3fb950', fontSize: '11px' }}>✓ Set</span>}
                </label>
                <input
                  type="text"
                  value={alpacaApiKey}
                  onChange={(e) => setAlpacaApiKey(e.target.value)}
                  placeholder={settings?.alpaca_api_key || "Enter your Alpaca API key"}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    backgroundColor: '#0d1117',
                    border: '1px solid #30363d',
                    borderRadius: '6px',
                    color: '#c9d1d9',
                    fontSize: '14px',
                    fontFamily: 'monospace',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#8b949e', marginBottom: '8px' }}>
                  Alpaca Secret Key {settings?.alpaca_secret_key_set && <span style={{ color: '#3fb950', fontSize: '11px' }}>✓ Set</span>}
                </label>
                <input
                  type="password"
                  value={alpacaSecretKey}
                  onChange={(e) => setAlpacaSecretKey(e.target.value)}
                  placeholder="Enter your Alpaca Secret key"
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    backgroundColor: '#0d1117',
                    border: '1px solid #30363d',
                    borderRadius: '6px',
                    color: '#c9d1d9',
                    fontSize: '14px',
                    fontFamily: 'monospace',
                    outline: 'none'
                  }}
                />
              </div>

              <button
                onClick={handleSaveKeys}
                disabled={updateKeysMutation.isPending}
                style={{
                  padding: '10px 16px',
                  borderRadius: '6px',
                  fontWeight: 600,
                  border: 'none',
                  cursor: updateKeysMutation.isPending ? 'not-allowed' : 'pointer',
                  backgroundColor: '#58a6ff',
                  color: '#ffffff',
                  opacity: updateKeysMutation.isPending ? 0.5 : 1
                }}
              >
                {updateKeysMutation.isPending ? 'Saving...' : 'Save API Keys'}
              </button>

              {updateKeysMutation.isSuccess && (
                <div style={{ backgroundColor: 'rgba(63, 185, 80, 0.1)', border: '1px solid rgba(63, 185, 80, 0.3)', borderRadius: '6px', padding: '10px 16px', color: '#3fb950', fontSize: '13px' }}>
                  API keys saved successfully!
                </div>
              )}
            </div>
          </div>

          {/* Risk Management */}
          <div style={{ backgroundColor: '#161b22', border: '1px solid #30363d', borderRadius: '8px', padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
              <Shield style={{ width: '20px', height: '20px', color: '#58a6ff' }} />
              <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#c9d1d9', margin: 0 }}>Risk Management</h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#8b949e', marginBottom: '8px' }}>
                  Max Position Size ($)
                </label>
                <input
                  type="number"
                  value={maxPositionSize}
                  onChange={(e) => setMaxPositionSize(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    backgroundColor: '#0d1117',
                    border: '1px solid #30363d',
                    borderRadius: '6px',
                    color: '#c9d1d9',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#8b949e', marginBottom: '8px' }}>
                  Max Daily Loss ($)
                </label>
                <input
                  type="number"
                  value={maxDailyLoss}
                  onChange={(e) => setMaxDailyLoss(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    backgroundColor: '#0d1117',
                    border: '1px solid #30363d',
                    borderRadius: '6px',
                    color: '#c9d1d9',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#8b949e', marginBottom: '8px' }}>
                  Stop Loss (%)
                </label>
                <input
                  type="number"
                  value={stopLoss}
                  onChange={(e) => setStopLoss(e.target.value)}
                  step="0.1"
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    backgroundColor: '#0d1117',
                    border: '1px solid #30363d',
                    borderRadius: '6px',
                    color: '#c9d1d9',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#8b949e', marginBottom: '8px' }}>
                  Take Profit (%)
                </label>
                <input
                  type="number"
                  value={takeProfit}
                  onChange={(e) => setTakeProfit(e.target.value)}
                  step="0.1"
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    backgroundColor: '#0d1117',
                    border: '1px solid #30363d',
                    borderRadius: '6px',
                    color: '#c9d1d9',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                />
              </div>
            </div>

            <button
              onClick={handleSaveRisk}
              disabled={updateRiskMutation.isPending}
              style={{
                marginTop: '16px',
                padding: '10px 16px',
                borderRadius: '6px',
                fontWeight: 600,
                border: 'none',
                cursor: updateRiskMutation.isPending ? 'not-allowed' : 'pointer',
                backgroundColor: '#58a6ff',
                color: '#ffffff',
                opacity: updateRiskMutation.isPending ? 0.5 : 1
              }}
            >
              {updateRiskMutation.isPending ? 'Saving...' : 'Save Risk Settings'}
            </button>

            {updateRiskMutation.isSuccess && (
              <div style={{ marginTop: '12px', backgroundColor: 'rgba(63, 185, 80, 0.1)', border: '1px solid rgba(63, 185, 80, 0.3)', borderRadius: '6px', padding: '10px 16px', color: '#3fb950', fontSize: '13px' }}>
                Risk settings saved successfully!
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}
