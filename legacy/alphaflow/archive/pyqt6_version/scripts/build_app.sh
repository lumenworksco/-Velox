#!/bin/bash
# ============================================================================
# AlphaFlow - Build Native macOS App Bundle
# Creates a distributable .app bundle using PyInstaller
# ============================================================================

set -e

echo "🚀 Building AlphaFlow Native macOS App..."
echo "=========================================="

# Get project directory (parent of scripts/)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Configuration
APP_NAME="AlphaFlow"
VERSION="1.0.0"
BUNDLE_ID="com.alignproject.alphaflow"
BUILD_DIR="$PROJECT_DIR/build"
DIST_DIR="$PROJECT_DIR/dist"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf "$BUILD_DIR" "$DIST_DIR" 2>/dev/null || true

# Check for required tools
echo "📋 Checking requirements..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install/update PyInstaller
echo "📦 Installing PyInstaller..."
pip3 install --upgrade pyinstaller

# Install app dependencies
echo "📦 Installing app dependencies..."
pip3 install -r requirements.txt
pip3 install PyQt6 PyQt6-Charts

# Create resources directory
mkdir -p "$PROJECT_DIR/resources"

# Create app icon
echo "🎨 Creating app icon..."
python3 << 'EOF'
import os
os.makedirs('resources', exist_ok=True)

try:
    from PIL import Image, ImageDraw
    
    size = 512
    img = Image.new('RGBA', (size, size), (13, 17, 23, 255))
    draw = ImageDraw.Draw(img)
    
    margin = size // 8
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size // 10,
        fill=(22, 27, 34, 255)
    )
    
    bar_count = 4
    bar_width = (size - 4 * margin) // (bar_count * 2)
    heights = [0.4, 0.7, 0.5, 0.9]
    
    for i, h in enumerate(heights):
        x = margin * 2 + i * bar_width * 2
        bar_height = int((size - 4 * margin) * h)
        y = size - margin * 2 - bar_height
        draw.rectangle(
            [x, y, x + bar_width, size - margin * 2],
            fill=(63, 185, 80, 255)
        )
    
    img.save('resources/icon.png', 'PNG')
    print("✅ Created icon")
except:
    print("⚠️ PIL not available, skipping icon creation")
EOF

# Create the PyInstaller spec file
echo "📝 Creating PyInstaller spec file..."
cat > "$PROJECT_DIR/AlphaFlow.spec" << 'SPEC'
# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None
spec_dir = os.path.dirname(os.path.abspath(SPECPATH))

# Data files to include (using new folder structure)
datas = [
    # Core trading modules
    ('core/__init__.py', 'core'),
    ('core/config.py', 'core'),
    ('core/data_structures.py', 'core'),
    ('core/trading_engine.py', 'core'),
    ('core/data_fetcher.py', 'core'),
    ('core/indicators.py', 'core'),
    ('core/strategies.py', 'core'),
    ('core/ml_predictor.py', 'core'),
    ('core/risk_manager.py', 'core'),
    ('core/portfolio_manager.py', 'core'),
    ('core/backtester.py', 'core'),
    ('core/deep_learning.py', 'core'),
    ('core/multi_timeframe.py', 'core'),
    ('core/options_trading.py', 'core'),
    ('core/sentiment_analysis.py', 'core'),
    # Config
    ('requirements.txt', '.'),
]

a = Analysis(
    ['app/alphaflow_mac.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtCharts',
        'pandas',
        'numpy',
        'yfinance',
        'sklearn',
        'sklearn.ensemble',
        'sklearn.preprocessing',
        'scipy',
        'scipy.stats',
        'core',
        'core.config',
        'core.data_structures',
        'core.data_fetcher',
        'core.indicators',
        'core.ml_predictor',
        'core.strategies',
        'core.trading_engine',
        'core.risk_manager',
        'core.portfolio_manager',
        'core.backtester',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'IPython', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AlphaFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AlphaFlow',
)

# Try to use icon if it exists
icon_path = 'resources/icon.png' if os.path.exists('resources/icon.png') else None

app = BUNDLE(
    coll,
    name='AlphaFlow.app',
    icon=icon_path,
    bundle_identifier='com.alignproject.alphaflow',
    info_plist={
        'CFBundleName': 'AlphaFlow',
        'CFBundleDisplayName': 'AlphaFlow',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.alignproject.alphaflow',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'ALFA',
        'LSMinimumSystemVersion': '10.15.0',
        'LSApplicationCategoryType': 'public.app-category.finance',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'NSHumanReadableCopyright': '© 2024-2026 The Align Project',
    },
)
SPEC

# Build the app
echo "🔨 Building app bundle (this may take a few minutes)..."
python3 -m PyInstaller --clean --noconfirm AlphaFlow.spec

# Check if build succeeded
if [ -d "$DIST_DIR/AlphaFlow.app" ]; then
    echo ""
    echo "============================================"
    echo "✅ BUILD SUCCESSFUL!"
    echo "============================================"
    echo ""
    echo "📁 App location: $DIST_DIR/AlphaFlow.app"
    echo ""
    echo "To install:"
    echo "  cp -r dist/AlphaFlow.app /Applications/"
    echo ""
    echo "To create DMG for distribution:"
    echo "  ./scripts/build_dmg.sh"
    echo ""
    
    # Open the dist folder
    open "$DIST_DIR"
else
    echo "❌ Build failed!"
    exit 1
fi
