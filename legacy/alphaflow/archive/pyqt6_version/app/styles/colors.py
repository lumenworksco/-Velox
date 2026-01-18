"""Bloomberg-inspired color palette for AlphaFlow."""

# ============================================================================
# BLOOMBERG TERMINAL COLOR PALETTE
# ============================================================================

BLOOMBERG_COLORS = {
    # Backgrounds
    'bg_primary': '#181A1B',      # Main background (slightly lighter than pure black)
    'bg_secondary': '#232526',    # Cards/Panels
    'bg_tertiary': '#2A2D31',     # Elevated surfaces
    'bg_hover': '#323639',        # Interactive hover
    'bg_elevated': '#23272E',     # Modal/dropdown background

    # Semantic data colors (color-blind accessible)
    'positive': '#00C676',         # Green (bullish)
    'negative': '#FF5247',         # Red (bearish)
    'neutral': '#5B9FFF',          # Blue (neutral/info)
    'warning': '#FFB946',          # Amber (alerts)
    'success': '#00D26A',          # Green (confirmation)

    # Text colors
    'text_primary': '#F3F6F9',     # Primary text
    'text_secondary': '#A0A4A8',   # Secondary/metadata
    'text_tertiary': '#6B7077',    # Disabled/faded

    # UI Elements
    'border': '#31363B',           # Dividers/borders
    'border_light': '#3F454C',     # Subtle borders
    'accent': '#00D26A',           # Primary accent (green)
    'accent_alt': '#3A8DFF',       # Secondary accent (blue)
    'accent_gold': '#FFA028',      # Bloomberg signature amber/gold

    # Chart colors
    'chart_bull_candle': '#00D26A',
    'chart_bear_candle': '#FF4757',
    'chart_line': '#3A8DFF',
    'chart_grid': '#31363B',
}

# Aliases for semantic usage
COLORS = BLOOMBERG_COLORS

# Signal badge colors
SIGNAL_COLORS = {
    'BUY': COLORS['positive'],
    'SELL': COLORS['negative'],
    'HOLD': COLORS['neutral'],
}

# Status colors
STATUS_COLORS = {
    'CONNECTED': COLORS['success'],
    'DISCONNECTED': COLORS['negative'],
    'CONNECTING': COLORS['warning'],
}
