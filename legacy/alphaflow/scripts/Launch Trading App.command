#!/bin/bash
# AlphaFlow - Native macOS App Launcher

# Get the project root directory (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Check for virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    PYTHON=".venv/bin/python"
else
    # Fallback to system Python
    export PATH="/Library/Frameworks/Python.framework/Versions/3.13/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:/Library/Frameworks/Python.framework/Versions/3.11/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
    PYTHON="python3"
fi

# Kill any existing Streamlit servers
pkill -f "streamlit run" 2>/dev/null

# Check for PyQt6-Charts
$PYTHON -c "import PyQt6.QtCharts" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing PyQt6-Charts (first time setup)..."
    $PYTHON -m pip install PyQt6 PyQt6-Charts
fi

# Launch the native macOS app
echo "🚀 Starting AlphaFlow..."
$PYTHON app/alphaflow_mac.py
