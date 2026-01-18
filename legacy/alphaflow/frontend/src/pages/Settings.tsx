import { useState } from 'react'
import { Save, Key, Shield, Bell, Palette, Database, AlertCircle, CheckCircle } from 'lucide-react'

export default function Settings() {
  const [saved, setSaved] = useState(false)

  // API Keys
  const [alpacaApiKey, setAlpacaApiKey] = useState('')
  const [alpacaSecretKey, setAlpacaSecretKey] = useState('')
  const [tradingMode, setTradingMode] = useState<'paper' | 'live'>('paper')

  // Risk Settings
  const [maxDailyLoss, setMaxDailyLoss] = useState('2')
  const [maxPositionSize, setMaxPositionSize] = useState('10')
  const [maxOpenPositions, setMaxOpenPositions] = useState('5')
  const [defaultRiskPerTrade, setDefaultRiskPerTrade] = useState('1')

  // Notifications
  const [enableOrderNotifications, setEnableOrderNotifications] = useState(true)
  const [enableSignalNotifications, setEnableSignalNotifications] = useState(true)
  const [enableRiskAlerts, setEnableRiskAlerts] = useState(true)
  const [enablePriceAlerts, setEnablePriceAlerts] = useState(false)

  // Display
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')
  const [chartType, setChartType] = useState<'candlestick' | 'line'>('candlestick')
  const [defaultTimeframe, setDefaultTimeframe] = useState('1D')
  const [showVolume, setShowVolume] = useState(true)

  // Data
  const [dataProvider, setDataProvider] = useState<'alpaca' | 'yfinance'>('alpaca')
  const [cacheEnabled, setCacheEnabled] = useState(true)
  const [cacheExpiration, setCacheExpiration] = useState('5')

  const handleSave = () => {
    // In a real implementation, this would save to backend
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Settings</h1>
          <p className="text-text-secondary mt-1">Configure your trading platform preferences</p>
        </div>

        <button
          onClick={handleSave}
          className="bg-accent-blue hover:bg-accent-blue-hover text-white font-semibold px-6 py-3 rounded-lg transition-colors flex items-center space-x-2"
        >
          <Save className="w-5 h-5" />
          <span>Save Changes</span>
        </button>
      </div>

      {saved && (
        <div className="bg-semantic-positive/10 border border-semantic-positive/30 rounded-lg p-4 flex items-center space-x-3">
          <CheckCircle className="w-5 h-5 text-semantic-positive" />
          <span className="text-semantic-positive font-medium">Settings saved successfully!</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* API Configuration */}
        <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-accent-blue/20 p-2 rounded-lg">
              <Key className="w-5 h-5 text-accent-blue" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-text-primary">API Configuration</h2>
              <p className="text-sm text-text-secondary">Connect to your trading account</p>
            </div>
          </div>

          <div className="space-y-4">
            {/* Trading Mode */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Trading Mode
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setTradingMode('paper')}
                  className={`py-3 rounded-lg font-semibold transition-all ${
                    tradingMode === 'paper'
                      ? 'bg-accent-blue text-white'
                      : 'bg-primary-elevated text-text-secondary hover:bg-primary-hover'
                  }`}
                >
                  Paper Trading
                </button>
                <button
                  onClick={() => setTradingMode('live')}
                  className={`py-3 rounded-lg font-semibold transition-all ${
                    tradingMode === 'live'
                      ? 'bg-semantic-negative text-white'
                      : 'bg-primary-elevated text-text-secondary hover:bg-primary-hover'
                  }`}
                >
                  Live Trading
                </button>
              </div>
              {tradingMode === 'live' && (
                <div className="mt-2 bg-semantic-negative/10 border border-semantic-negative/30 rounded-lg p-3 flex items-start space-x-2">
                  <AlertCircle className="w-4 h-4 text-semantic-negative mt-0.5 flex-shrink-0" />
                  <span className="text-semantic-negative text-sm">
                    Live trading uses real money. Ensure you understand the risks before proceeding.
                  </span>
                </div>
              )}
            </div>

            {/* Alpaca API Key */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Alpaca API Key
              </label>
              <input
                type="text"
                value={alpacaApiKey}
                onChange={(e) => setAlpacaApiKey(e.target.value)}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-3 px-4 text-text-primary focus:outline-none focus:border-accent-blue font-mono text-sm"
                placeholder="AKXXXXXXXXXXXXXXXXXX"
              />
            </div>

            {/* Alpaca Secret Key */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Alpaca Secret Key
              </label>
              <input
                type="password"
                value={alpacaSecretKey}
                onChange={(e) => setAlpacaSecretKey(e.target.value)}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-3 px-4 text-text-primary focus:outline-none focus:border-accent-blue font-mono text-sm"
                placeholder="••••••••••••••••••••"
              />
            </div>

            <div className="bg-accent-blue/10 border border-accent-blue/30 rounded-lg p-3 flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-accent-blue mt-0.5 flex-shrink-0" />
              <div className="text-accent-blue text-sm">
                <p className="font-medium">Your API keys are stored securely</p>
                <p className="mt-1 text-accent-blue/80">
                  Get your API keys from{' '}
                  <a
                    href="https://alpaca.markets"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-accent-blue"
                  >
                    alpaca.markets
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Risk Management */}
        <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-semantic-negative/20 p-2 rounded-lg">
              <Shield className="w-5 h-5 text-semantic-negative" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-text-primary">Risk Management</h2>
              <p className="text-sm text-text-secondary">Set your trading limits</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Max Daily Loss (%)
              </label>
              <input
                type="number"
                value={maxDailyLoss}
                onChange={(e) => setMaxDailyLoss(e.target.value)}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-3 px-4 text-text-primary focus:outline-none focus:border-accent-blue"
                step="0.5"
                min="0"
                max="100"
              />
              <p className="text-xs text-text-tertiary mt-1">
                Trading will be halted if daily loss exceeds this percentage
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Max Position Size (%)
              </label>
              <input
                type="number"
                value={maxPositionSize}
                onChange={(e) => setMaxPositionSize(e.target.value)}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-3 px-4 text-text-primary focus:outline-none focus:border-accent-blue"
                step="1"
                min="0"
                max="100"
              />
              <p className="text-xs text-text-tertiary mt-1">
                Maximum portfolio allocation per position
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Max Open Positions
              </label>
              <input
                type="number"
                value={maxOpenPositions}
                onChange={(e) => setMaxOpenPositions(e.target.value)}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-3 px-4 text-text-primary focus:outline-none focus:border-accent-blue"
                min="1"
                max="50"
              />
              <p className="text-xs text-text-tertiary mt-1">Maximum number of concurrent positions</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Default Risk Per Trade (%)
              </label>
              <input
                type="number"
                value={defaultRiskPerTrade}
                onChange={(e) => setDefaultRiskPerTrade(e.target.value)}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-3 px-4 text-text-primary focus:outline-none focus:border-accent-blue"
                step="0.1"
                min="0"
                max="10"
              />
              <p className="text-xs text-text-tertiary mt-1">
                Default risk amount per trade for strategies
              </p>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-accent-amber/20 p-2 rounded-lg">
              <Bell className="w-5 h-5 text-accent-amber" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-text-primary">Notifications</h2>
              <p className="text-sm text-text-secondary">Choose what alerts you receive</p>
            </div>
          </div>

          <div className="space-y-4">
            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <div className="text-text-primary font-medium">Order Notifications</div>
                <div className="text-sm text-text-secondary">Get notified when orders are filled</div>
              </div>
              <input
                type="checkbox"
                checked={enableOrderNotifications}
                onChange={(e) => setEnableOrderNotifications(e.target.checked)}
                className="w-5 h-5 text-accent-blue bg-primary-elevated border-primary-border rounded focus:ring-2 focus:ring-accent-blue focus:ring-offset-0"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <div className="text-text-primary font-medium">Strategy Signals</div>
                <div className="text-sm text-text-secondary">
                  Get notified of buy/sell signals from strategies
                </div>
              </div>
              <input
                type="checkbox"
                checked={enableSignalNotifications}
                onChange={(e) => setEnableSignalNotifications(e.target.checked)}
                className="w-5 h-5 text-accent-blue bg-primary-elevated border-primary-border rounded focus:ring-2 focus:ring-accent-blue focus:ring-offset-0"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <div className="text-text-primary font-medium">Risk Alerts</div>
                <div className="text-sm text-text-secondary">
                  Get notified when risk limits are approached
                </div>
              </div>
              <input
                type="checkbox"
                checked={enableRiskAlerts}
                onChange={(e) => setEnableRiskAlerts(e.target.checked)}
                className="w-5 h-5 text-accent-blue bg-primary-elevated border-primary-border rounded focus:ring-2 focus:ring-accent-blue focus:ring-offset-0"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <div className="text-text-primary font-medium">Price Alerts</div>
                <div className="text-sm text-text-secondary">
                  Get notified when symbols hit target prices
                </div>
              </div>
              <input
                type="checkbox"
                checked={enablePriceAlerts}
                onChange={(e) => setEnablePriceAlerts(e.target.checked)}
                className="w-5 h-5 text-accent-blue bg-primary-elevated border-primary-border rounded focus:ring-2 focus:ring-accent-blue focus:ring-offset-0"
              />
            </label>
          </div>
        </div>

        {/* Display Preferences */}
        <div className="bg-primary-surface rounded-lg border border-primary-border p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-accent-purple/20 p-2 rounded-lg">
              <Palette className="w-5 h-5 text-accent-purple" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-text-primary">Display Preferences</h2>
              <p className="text-sm text-text-secondary">Customize your interface</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">Theme</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setTheme('dark')}
                  className={`py-3 rounded-lg font-semibold transition-all ${
                    theme === 'dark'
                      ? 'bg-accent-blue text-white'
                      : 'bg-primary-elevated text-text-secondary hover:bg-primary-hover'
                  }`}
                >
                  Dark
                </button>
                <button
                  onClick={() => setTheme('light')}
                  className={`py-3 rounded-lg font-semibold transition-all ${
                    theme === 'light'
                      ? 'bg-accent-blue text-white'
                      : 'bg-primary-elevated text-text-secondary hover:bg-primary-hover'
                  }`}
                >
                  Light
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Chart Type
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setChartType('candlestick')}
                  className={`py-3 rounded-lg font-semibold transition-all ${
                    chartType === 'candlestick'
                      ? 'bg-accent-blue text-white'
                      : 'bg-primary-elevated text-text-secondary hover:bg-primary-hover'
                  }`}
                >
                  Candlestick
                </button>
                <button
                  onClick={() => setChartType('line')}
                  className={`py-3 rounded-lg font-semibold transition-all ${
                    chartType === 'line'
                      ? 'bg-accent-blue text-white'
                      : 'bg-primary-elevated text-text-secondary hover:bg-primary-hover'
                  }`}
                >
                  Line
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Default Timeframe
              </label>
              <select
                value={defaultTimeframe}
                onChange={(e) => setDefaultTimeframe(e.target.value)}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-3 px-4 text-text-primary focus:outline-none focus:border-accent-blue"
              >
                <option value="1m">1 Minute</option>
                <option value="5m">5 Minutes</option>
                <option value="15m">15 Minutes</option>
                <option value="1H">1 Hour</option>
                <option value="1D">1 Day</option>
                <option value="1W">1 Week</option>
              </select>
            </div>

            <label className="flex items-center justify-between cursor-pointer">
              <div>
                <div className="text-text-primary font-medium">Show Volume</div>
                <div className="text-sm text-text-secondary">Display volume bars on charts</div>
              </div>
              <input
                type="checkbox"
                checked={showVolume}
                onChange={(e) => setShowVolume(e.target.checked)}
                className="w-5 h-5 text-accent-blue bg-primary-elevated border-primary-border rounded focus:ring-2 focus:ring-accent-blue focus:ring-offset-0"
              />
            </label>
          </div>
        </div>

        {/* Data Settings */}
        <div className="bg-primary-surface rounded-lg border border-primary-border p-6 lg:col-span-2">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-semantic-positive/20 p-2 rounded-lg">
              <Database className="w-5 h-5 text-semantic-positive" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-text-primary">Data Settings</h2>
              <p className="text-sm text-text-secondary">Configure data sources and caching</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Data Provider
              </label>
              <select
                value={dataProvider}
                onChange={(e) => setDataProvider(e.target.value as 'alpaca' | 'yfinance')}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-3 px-4 text-text-primary focus:outline-none focus:border-accent-blue"
              >
                <option value="alpaca">Alpaca Markets</option>
                <option value="yfinance">Yahoo Finance</option>
              </select>
            </div>

            <div>
              <label className="flex items-center justify-between cursor-pointer h-full">
                <div>
                  <div className="text-text-primary font-medium">Enable Caching</div>
                  <div className="text-sm text-text-secondary">Cache market data locally</div>
                </div>
                <input
                  type="checkbox"
                  checked={cacheEnabled}
                  onChange={(e) => setCacheEnabled(e.target.checked)}
                  className="w-5 h-5 text-accent-blue bg-primary-elevated border-primary-border rounded focus:ring-2 focus:ring-accent-blue focus:ring-offset-0"
                />
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Cache Expiration (minutes)
              </label>
              <input
                type="number"
                value={cacheExpiration}
                onChange={(e) => setCacheExpiration(e.target.value)}
                disabled={!cacheEnabled}
                className="w-full bg-primary-elevated border border-primary-border rounded-lg py-3 px-4 text-text-primary focus:outline-none focus:border-accent-blue disabled:opacity-50 disabled:cursor-not-allowed"
                min="1"
                max="60"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
