/**
 * Professional Financial Terminal Color Palette
 * Inspired by Bloomberg Terminal and Saxo Bank Trader
 */

export const colors = {
  // Background colors - Deep navy/black for professional look
  background: {
    primary: '#0a0e27',      // Main background - deep navy
    secondary: '#0f1629',    // Cards and panels - slightly lighter navy
    tertiary: '#1a1f3a',     // Hover states and elevated surfaces
    overlay: 'rgba(10, 14, 39, 0.95)', // Modal backdrop
  },

  // Border colors
  border: {
    primary: '#1e2442',      // Subtle borders
    secondary: '#2a3150',    // More prominent borders
    accent: '#3d4463',       // Focused/active borders
  },

  // Text colors
  text: {
    primary: '#e5e7eb',      // Main text - bright white
    secondary: '#9ca3af',    // Muted text - gray
    tertiary: '#6b7280',     // Very muted - darker gray
    inverse: '#0a0e27',      // Dark text on light bg
  },

  // Accent colors - Professional amber/orange (Bloomberg signature)
  accent: {
    primary: '#ff8c00',      // Bloomberg orange
    secondary: '#ffa500',    // Lighter orange
    hover: '#ff9500',        // Hover state
    muted: 'rgba(255, 140, 0, 0.1)',  // Transparent version
  },

  // Financial data colors
  financial: {
    positive: '#10b981',     // Green for gains
    negative: '#ef4444',     // Red for losses
    neutral: '#6b7280',      // Gray for neutral
    positiveBg: 'rgba(16, 185, 129, 0.1)',
    negativeBg: 'rgba(239, 68, 68, 0.1)',
  },

  // Status colors
  status: {
    active: '#10b981',       // Green - running
    paused: '#f59e0b',       // Amber - paused
    stopped: '#6b7280',      // Gray - stopped
    error: '#ef4444',        // Red - error
    warning: '#f59e0b',      // Amber - warning
    info: '#3b82f6',         // Blue - info
  },

  // Interactive elements
  interactive: {
    primary: '#3b82f6',      // Primary blue
    hover: '#2563eb',        // Darker blue
    active: '#1d4ed8',       // Even darker
    disabled: '#4b5563',     // Gray
  },

  // Button colors
  button: {
    buy: '#10b981',          // Green
    buyHover: '#059669',
    sell: '#ef4444',         // Red
    sellHover: '#dc2626',
    primary: '#ff8c00',      // Bloomberg orange
    primaryHover: '#ff9500',
    secondary: '#1a1f3a',
    secondaryHover: '#2a3150',
  },

  // Chart colors
  chart: {
    grid: '#1e2442',         // Grid lines
    axis: '#6b7280',         // Axis labels
    candleUp: '#10b981',     // Green candle
    candleDown: '#ef4444',   // Red candle
    volume: '#3b82f6',       // Volume bars
    ma: '#f59e0b',           // Moving average line
    indicator: '#8b5cf6',    // Other indicators
  },

  // Data table colors
  table: {
    header: '#0f1629',
    row: '#0a0e27',
    rowAlt: '#0f1629',
    rowHover: '#1a1f3a',
    border: '#1e2442',
  },
}

// Font configurations
export const fonts = {
  mono: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace',
  sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", sans-serif',
}

// Spacing scale (consistent with financial terminals)
export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  xxl: '32px',
}

// Border radius
export const borderRadius = {
  sm: '4px',
  md: '6px',
  lg: '8px',
  xl: '12px',
}

// Shadows for depth
export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.5)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.5)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
}

// Animation durations
export const transitions = {
  fast: '150ms',
  normal: '200ms',
  slow: '300ms',
}
