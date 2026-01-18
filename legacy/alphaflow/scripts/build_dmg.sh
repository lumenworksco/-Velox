#!/bin/bash
# ============================================================================
# AlphaFlow - Create DMG Installer
# Creates a professional DMG disk image for distribution
# ============================================================================

set -e

echo "📦 Creating AlphaFlow DMG Installer..."
echo "======================================="

# Get project directory (parent of scripts/)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Configuration
APP_NAME="AlphaFlow"
VERSION="1.0.0"
DMG_NAME="${APP_NAME}-${VERSION}"
DIST_DIR="$PROJECT_DIR/dist"
APP_PATH="$DIST_DIR/AlphaFlow.app"
DMG_PATH="$DIST_DIR/${DMG_NAME}.dmg"
DMG_TEMP="$DIST_DIR/${DMG_NAME}-temp.dmg"
VOLUME_NAME="$APP_NAME $VERSION"

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "❌ AlphaFlow.app not found in dist/"
    echo "   Run ./build_app.sh first"
    exit 1
fi

# Remove old DMG if exists
rm -f "$DMG_PATH" "$DMG_TEMP"

# Get app size and calculate DMG size
APP_SIZE=$(du -sm "$APP_PATH" | cut -f1)
DMG_SIZE=$((APP_SIZE + 50))

echo "📊 App size: ${APP_SIZE}MB"
echo "📀 Creating ${DMG_SIZE}MB DMG..."

# Create temporary DMG
hdiutil create -srcfolder "$APP_PATH" -volname "$VOLUME_NAME" -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${DMG_SIZE}m "$DMG_TEMP"

# Mount the temporary DMG
echo "🔧 Customizing DMG..."
MOUNT_DIR=$(hdiutil attach -readwrite -noverify "$DMG_TEMP" | \
    egrep '^/dev/' | sed 1q | awk '{print $NF}')

if [ -z "$MOUNT_DIR" ]; then
    echo "❌ Failed to mount DMG"
    exit 1
fi

# Create Applications symlink
ln -s /Applications "$MOUNT_DIR/Applications"

# Create background folder and add instructions
mkdir -p "$MOUNT_DIR/.background"

# Create a simple README
cat > "$MOUNT_DIR/README.txt" << 'README'
AlphaFlow - Algorithmic Trading Platform
=========================================

Installation:
1. Drag AlphaFlow.app to the Applications folder
2. Double-click AlphaFlow in Applications to launch

First Launch:
- macOS may show a security warning
- Go to System Preferences > Security & Privacy
- Click "Open Anyway" to allow AlphaFlow

Requirements:
- macOS 10.15 (Catalina) or later
- Internet connection for market data

Support:
https://github.com/The-Align-Project/Trading-Algorithm

© 2024-2026 The Align Project
README

# Set DMG window properties using AppleScript
echo "🎨 Setting DMG appearance..."
osascript << APPLESCRIPT
tell application "Finder"
    tell disk "$VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set bounds of container window to {400, 100, 920, 440}
        set viewOptions to icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 80
        set position of item "AlphaFlow.app" of container window to {130, 150}
        set position of item "Applications" of container window to {390, 150}
        set position of item "README.txt" of container window to {260, 280}
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
APPLESCRIPT

# Sync and unmount
sync
hdiutil detach "$MOUNT_DIR"

# Convert to compressed DMG
echo "🗜️ Compressing DMG..."
hdiutil convert "$DMG_TEMP" -format UDZO -imagekey zlib-level=9 -o "$DMG_PATH"

# Clean up
rm -f "$DMG_TEMP"

# Verify
if [ -f "$DMG_PATH" ]; then
    DMG_FINAL_SIZE=$(du -h "$DMG_PATH" | cut -f1)
    echo ""
    echo "============================================"
    echo "✅ DMG CREATED SUCCESSFULLY!"
    echo "============================================"
    echo ""
    echo "📀 DMG: $DMG_PATH"
    echo "📊 Size: $DMG_FINAL_SIZE"
    echo ""
    echo "The DMG is ready for distribution!"
    echo ""
    
    # Open the dist folder
    open "$DIST_DIR"
else
    echo "❌ Failed to create DMG"
    exit 1
fi
