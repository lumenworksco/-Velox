#!/usr/bin/env python3
"""
AlphaFlow - Main Entry Point
Launches the native macOS trading application.
"""

import sys
import os

# Add project root to path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

if __name__ == "__main__":
    from app.alphaflow_mac import main
    main()
